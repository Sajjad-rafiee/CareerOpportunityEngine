"""Fetch real N26 postings from Greenhouse, normalize, write to JSON.
No database involved.

Run: uv run python -m scripts.fetch_greenhouse
"""

import json
import logging
from pathlib import Path

from app.adapters.greenhouse import GreenhouseAPIError, fetch_opportunities
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "opportunities_greenhouse.json"

BOARD_TOKEN = "n26"
ORGANIZATION_NAME = "N26"


def main() -> None:
    setup_logging()

    try:
        opportunities = fetch_opportunities(
            board_token=BOARD_TOKEN, organization_name=ORGANIZATION_NAME
        )
    except GreenhouseAPIError:
        logger.exception("Failed to fetch from Greenhouse")
        raise SystemExit(1) from None

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    payload = [o.model_dump(mode="json") for o in opportunities]
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    logger.info("Saved %d opportunities to %s", len(opportunities), OUTPUT_PATH)


if __name__ == "__main__":
    main()
