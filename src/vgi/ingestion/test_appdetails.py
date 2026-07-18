"""
Small-sample test of Steam's Storefront appdetails endpoint.
Goal: observe real response shape and behavior before scaling to the
full 23,066-game Gold-tier candidate list.
"""

import json
import sys
import time
from pathlib import Path

import httpx
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT, STEAM_APP_DETAILS_URL

SAMPLE_SIZE = 20
REQUEST_DELAY_SECONDS = 1.5  # conservative starting guess, unofficial endpoint


def fetch_appdetails(appid: int) -> dict:
    response = httpx.get(
        STEAM_APP_DETAILS_URL,
        params={"appids": appid},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()


def main():
    candidates_path = PROJECT_ROOT / "data" / "interim" / "gold_candidates.parquet"
    candidates_df = pd.read_parquet(candidates_path)

    sample = candidates_df.head(SAMPLE_SIZE)
    print(f"Testing appdetails on {len(sample)} sample apps...")

    results = {}
    for _, row in sample.iterrows():
        appid = int(row["appid"])
        print(f"Fetching appid {appid} ({row['name']})...")

        try:
            data = fetch_appdetails(appid)
            results[appid] = data
        except Exception as e:
            print(f"  FAILED: {e}")
            results[appid] = {"error": str(e)}

        time.sleep(REQUEST_DELAY_SECONDS)

    # Save raw sample for inspection
    raw_dir = PROJECT_ROOT / "data" / "raw" / "steam"
    raw_dir.mkdir(parents=True, exist_ok=True)
    out_path = raw_dir / "appdetails_sample_test.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved raw sample to {out_path}")

    # Quick shape inspection
    success_count = sum(
        1 for v in results.values()
        if isinstance(v, dict) and v.get(str(list(v.keys())[0]) if False else None) is None
    )
    print("\n--- Response shape check ---")
    for appid, data in list(results.items())[:3]:
        if "error" in data:
            print(f"{appid}: ERROR - {data['error']}")
            continue
        inner = data.get(str(appid), {})
        print(f"{appid}: success={inner.get('success')}, top-level keys={list(inner.get('data', {}).keys())[:8] if inner.get('success') else 'N/A'}")


if __name__ == "__main__":
    main()