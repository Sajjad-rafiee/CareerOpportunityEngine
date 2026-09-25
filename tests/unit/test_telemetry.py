from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

import app.core.telemetry as telemetry_module
from app.core.telemetry import setup_telemetry
from app.services.opportunities import search_opportunities


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows


class FakeSession:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, _statement):
        return FakeResult(self._rows)


def _reset_global_tracer_provider(monkeypatch):
    """Undo OpenTelemetry's process-wide "set once" latch on the tracer provider.

    `trace.set_tracer_provider()` is guarded by an internal `Once` object, not
    just `_TRACER_PROVIDER` — resetting only the variable leaves later calls
    silently ignored, so each test needs both reset to get its own provider.
    """
    monkeypatch.setattr(trace, "_TRACER_PROVIDER", None)
    monkeypatch.setattr(trace, "_TRACER_PROVIDER_SET_ONCE", trace.Once())


def _real_tracer_provider(monkeypatch):
    _reset_global_tracer_provider(monkeypatch)
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    return exporter


def _stub_out_network_exporter(monkeypatch):
    """setup_telemetry() normally builds a network-bound OTLP exporter; these
    tests only exercise its own control flow, not a real collector."""
    monkeypatch.setattr(telemetry_module, "OTLPSpanExporter", lambda: InMemorySpanExporter())
    monkeypatch.setattr(telemetry_module, "BatchSpanProcessor", SimpleSpanProcessor)


def test_setup_telemetry_is_disabled_by_default(monkeypatch):
    monkeypatch.setattr(telemetry_module, "_enabled", None)
    monkeypatch.delenv("OTEL_TRACES_EXPORTER", raising=False)

    assert setup_telemetry(FastAPI()) is False


def test_setup_telemetry_enables_when_configured(monkeypatch):
    monkeypatch.setattr(telemetry_module, "_enabled", None)
    _reset_global_tracer_provider(monkeypatch)
    _stub_out_network_exporter(monkeypatch)
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "otlp")

    assert setup_telemetry(FastAPI()) is True


def test_setup_telemetry_is_idempotent(monkeypatch):
    monkeypatch.setattr(telemetry_module, "_enabled", None)
    _reset_global_tracer_provider(monkeypatch)
    _stub_out_network_exporter(monkeypatch)
    monkeypatch.setenv("OTEL_TRACES_EXPORTER", "otlp")

    setup_telemetry(FastAPI())
    provider_after_first_call = trace.get_tracer_provider()

    setup_telemetry(FastAPI())

    assert trace.get_tracer_provider() is provider_after_first_call


def test_fastapi_instrumentation_creates_request_span(monkeypatch):
    exporter = _real_tracer_provider(monkeypatch)
    test_app = FastAPI()

    @test_app.get("/ping")
    def ping():
        return {"ok": True}

    instrumentor = FastAPIInstrumentor()
    instrumentor.instrument_app(test_app)
    try:
        with TestClient(test_app) as client:
            response = client.get("/ping")
    finally:
        instrumentor.uninstrument_app(test_app)

    assert response.status_code == 200
    server_spans = [s for s in exporter.get_finished_spans() if s.kind.name == "SERVER"]
    assert len(server_spans) == 1


def test_search_opportunities_creates_search_span_with_safe_attributes(monkeypatch):
    exporter = _real_tracer_provider(monkeypatch)
    rows = [(f"fake-opportunity-{i}", 0.9 - i * 0.1) for i in range(3)]
    session = FakeSession(rows)

    search_opportunities(session, query_embedding=[0.0] * 384, limit=5)

    [span] = [s for s in exporter.get_finished_spans() if s.name == "opportunities.search"]
    assert span.attributes["search.limit"] == 5
    assert span.attributes["result.count"] == 3


def test_search_span_does_not_record_result_content(monkeypatch):
    exporter = _real_tracer_provider(monkeypatch)
    rows = [("SECRET_OPPORTUNITY_TITLE", 0.5)]
    session = FakeSession(rows)

    search_opportunities(session, query_embedding=[0.0] * 384, limit=1)

    [span] = [s for s in exporter.get_finished_spans() if s.name == "opportunities.search"]
    for value in span.attributes.values():
        assert "SECRET_OPPORTUNITY_TITLE" not in str(value)
