"""Optional OpenTelemetry tracing, off by default.

Mirrors JobDiscoveryAgent's `utils/telemetry.py`: a no-op unless
`OTEL_TRACES_EXPORTER=otlp`. When it's a no-op, spans created via
`get_tracer()` use the OpenTelemetry API's default no-op tracer provider —
no exporter, no network calls — so this is safe to leave wired in without
requiring Jaeger for normal use or tests.

Propagation uses OpenTelemetry's default W3C Trace Context + Baggage
propagators; the incoming `traceparent` header is extracted automatically by
the FastAPI/ASGI instrumentation, no custom propagation code is needed.
"""

import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

DEFAULT_SERVICE_NAME = "career-opportunity-engine"

_enabled: bool | None = None


def setup_telemetry(app: FastAPI) -> bool:
    """Configure the OpenTelemetry SDK and instrument `app` if tracing is
    enabled. Idempotent (later calls just return the first call's result).
    """
    global _enabled
    if _enabled is not None:
        return _enabled

    if os.environ.get("OTEL_TRACES_EXPORTER", "").strip().lower() != "otlp":
        _enabled = False
        return False

    service_name = os.environ.get("OTEL_SERVICE_NAME", DEFAULT_SERVICE_NAME)
    resource = Resource.create({"service.name": service_name})

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)

    _enabled = True
    return True


def get_tracer() -> trace.Tracer:
    return trace.get_tracer(DEFAULT_SERVICE_NAME)
