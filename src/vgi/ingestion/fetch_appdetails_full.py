"""
Full-scale appdetails ingestion, processed in batches of ~3,000 games.
Run this script repeatedly — it automatically resumes from wherever it left off,
processes one batch, then stops so progress can be verified before continuing.
"""

import json
import sys
import time
from pathlib import Path

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT, STEAM_APP_DETAILS_URL
from src.vgi.ingestion.parse_appdetails import AppDetailsParser
from src.vgi.resolution.entity_registry import EntityRegistry

BATCH_SIZE = 3000
REQUEST_DELAY_SECONDS = 1.5
RAW_JSONL_PATH = PROJECT_ROOT / "data" / "raw" / "steam" / "appdetails_all.jsonl"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type((httpx.HTTPError, json.JSONDecodeError)),
    reraise=True,
)
def fetch_one(appid: int) -> dict:
    response = httpx.get(STEAM_APP_DETAILS_URL, params={"appids": appid}, timeout=30.0)
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


def append_raw_record(appid: int, success: bool, data: dict | None, error: str | None = None):
    RAW_JSONL_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"appid": appid, "success": success, "data": data, "error": error}
    with open(RAW_JSONL_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def run_batch():
    candidates_path = INTERIM_DIR / "gold_candidates.parquet"
    candidates_df = pd.read_parquet(candidates_path)
    all_appids = candidates_df["appid"].astype(int).tolist()

    completed = load_completed_appids()
    remaining = [a for a in all_appids if a not in completed]

    print(f"Total Gold-tier candidates: {len(all_appids):,}")
    print(f"Already completed: {len(completed):,}")
    print(f"Remaining: {len(remaining):,}")

    if not remaining:
        print("All candidates already fetched. Nothing to do.")
        return

    batch = remaining[:BATCH_SIZE]
    print(f"\nProcessing this batch: {len(batch):,} games\n")

    success_count = 0
    fail_count = 0

    for i, appid in enumerate(batch, 1):
        try:
            response = fetch_one(appid)
            entry = response.get(str(appid), {})
            if entry.get("success"):
                append_raw_record(appid, True, entry.get("data"))
                success_count += 1
            else:
                append_raw_record(appid, False, None, error="success=false (delisted/region-locked/etc.)")
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