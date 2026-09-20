"""
از Greenhouse (شرکت N26) داده واقعی بگیر، normalize کن، و توی یک فایل
JSON بریز. دیتابیس اینجا اصلاً دخیل نیست.

اجرا: uv run python -m scripts.fetch_greenhouse
"""

import json
from pathlib import Path

from app.adapters.greenhouse import GreenhouseAPIError, fetch_opportunities

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "opportunities_greenhouse.json"

BOARD_TOKEN = "n26"
ORGANIZATION_NAME = "N26"


def main() -> None:
    try:
        opportunities = fetch_opportunities(
            board_token=BOARD_TOKEN, organization_name=ORGANIZATION_NAME
        )
    except GreenhouseAPIError as exc:
        print(f"Failed to fetch from Greenhouse: {exc}")
        raise SystemExit(1) from exc

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    payload = [o.model_dump(mode="json") for o in opportunities]
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False))

    print(f"Saved {len(opportunities)} opportunities to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
