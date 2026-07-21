"""
Full-scale Steam review summary ingestion, processed in batches of ~3,000 games.
Same battle-tested pattern as fetch_appdetails_full.py: checkpointed via JSONL,
resumable, conservative rate limiting.

Collects ONLY aggregate review summaries (review_score_desc, total counts) —
deliberately NOT individual review text/author data, per this project's data
ethics policy (see LICENSE_POLICY.md).
"""

import json
import sys
import time
from pathlib import Path

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

BATCH_SIZE = 3000
REQUEST_DELAY_SECONDS = 1.5
RAW_JSONL_PATH = PROJECT_ROOT / "data" / "raw" / "steam" / "review_summaries_all.jsonl"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type((httpx.HTTPError, json.JSONDecodeError)),
    reraise=True,
)
def fetch_review_summary(appid: int) -> dict:
    url = f"https://store.steampowered.com/appreviews/{appid}"
    params = {
        "json": 1,
        "filter": "recent",
        "language": "all",
        "review_type": "all",
        "purchase_type": "all",
        "num_per_page": 1,  # we only need query_summary, not review text
    }
    response = httpx.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return response.json()


def load_completed_appids() -> set[int]:
    if not RAW_JSONL_PATH.exists():
        return set()
    completed = set()
    with open(RAW_JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                record = json.loads(line)
                completed.add(record["appid"])
    return completed


def append_raw_record(appid: int, success: bool, summary: dict | None, error: str | None = None):
    RAW_JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"appid": appid, "success": success, "summary": summary, "error": error}
    with open(RAW_JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def run_batch():
    games_df = pd.read_parquet(PROCESSED_DIR / "games.parquet")
    all_appids = games_df["steam_appid"].astype(int).tolist()

    completed = load_completed_appids()
    remaining = [a for a in all_appids if a not in completed]

    print(f"Total Gold-tier games: {len(all_appids):,}")
    print(f"Already completed: {len(completed):,}")
    print(f"Remaining: {len(remaining):,}")

    if not remaining:
        print("All games already fetched. Nothing to do.")
        return

    batch = remaining[:BATCH_SIZE]
    print(f"\nProcessing this batch: {len(batch):,} games\n")

    success_count = 0
    fail_count = 0

    for i, appid in enumerate(batch, 1):
        try:
            response = fetch_review_summary(appid)
            if response.get("success") == 1:
                # Deliberately extract ONLY the aggregate summary, discard reviews list
                summary = response.get("query_summary", {})
                append_raw_record(appid, True, summary)
                success_count += 1
            else:
                append_raw_record(appid, False, None, error="success != 1 (no review data available)")
                fail_count += 1
        except Exception as e:
            append_raw_record(appid, False, None, error=str(e))
            fail_count += 1

        if i % 250 == 0:
            print(f"  ...{i:,}/{len(batch):,} in this batch ({success_count} ok, {fail_count} failed)")

        time.sleep(REQUEST_DELAY_SECONDS)

    print(f"\nBatch complete: {success_count:,} succeeded, {fail_count:,} failed.")
    print(f"Total progress: {len(completed) + len(batch):,} / {len(all_appids):,}")


if __name__ == "__main__":
    run_batch()