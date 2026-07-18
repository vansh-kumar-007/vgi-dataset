"""
Steam app list ingestion — sourced via SteamSpy (keyless, no purchase required).

IMPORTANT: SteamSpy's `all` request is rate-limited to 1 request PER MINUTE
(not per second — that limit applies to other SteamSpy endpoints only).
This is a slow, patient pull by design. Progress is checkpointed after every
page so a run can be resumed instead of restarted from scratch.
"""

import json
import time
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import RAW_DIR

STEAM_RAW_DIR = RAW_DIR / "steam"
STEAMSPY_URL = "https://steamspy.com/api.php"
REQUEST_DELAY_SECONDS = 60.0  # CORRECTED: SteamSpy's real 'all' endpoint limit


def checkpoint_path() -> Path:
    return STEAM_RAW_DIR / f"steamspy_all_{date.today().isoformat()}_INPROGRESS.json"


def load_checkpoint() -> list[dict]:
    """Resume from a previous partial run today, if one exists."""
    path = checkpoint_path()
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        print(f"Found existing checkpoint with {len(existing)} pages already saved. Resuming.")
        return existing
    return []


class SteamSpyServerBusyError(Exception):
    """Raised when SteamSpy returns HTTP 200 but a plain-text server error body."""
    pass


@retry(
    stop=stop_after_attempt(8),
    wait=wait_exponential(multiplier=1, min=10, max=180),  # patient: up to 3 min between tries
    retry=retry_if_exception_type((httpx.HTTPError, json.JSONDecodeError, SteamSpyServerBusyError)),
    reraise=True,
)
def fetch_steamspy_page(page: int) -> dict:
    params = {"request": "all", "page": page}
    response = httpx.get(STEAMSPY_URL, params=params, timeout=30.0)
    response.raise_for_status()

    # SteamSpy sometimes returns HTTP 200 with a plain-text server error body
    # instead of JSON (e.g. "Connection failed: Too many connections").
    # A 200 status alone doesn't guarantee a valid payload — check content.
    if response.text.strip().startswith("Connection failed"):
        raise SteamSpyServerBusyError(response.text.strip())

    return response.json()


def save_raw_pages(all_raw_pages: list[dict], suffix: str = "") -> Path:
    STEAM_RAW_DIR.mkdir(parents=True, exist_ok=True)
    out_path = STEAM_RAW_DIR / f"steamspy_all_{date.today().isoformat()}{suffix}.json"
    out_path.write_text(json.dumps(all_raw_pages), encoding="utf-8")
    return out_path


def fetch_all_pages(max_pages: int = 300) -> list[dict]:
    all_raw_pages = load_checkpoint()
    start_page = len(all_raw_pages)  # resume exactly where we left off

    for page in range(start_page, max_pages):
        print(f"Fetching SteamSpy page {page}... (this endpoint is limited to 1 req/minute)")

        try:
            page_data = fetch_steamspy_page(page)
        except (httpx.HTTPError, json.JSONDecodeError, SteamSpyServerBusyError) as e:
            print(f"Page {page} failed after all retries: {e}")
            print(f"Skipping page {page} for now — flagging for manual backfill later.")
            continue

        if not page_data:
            print(f"Page {page} was empty — stopping pagination (natural end reached).")
            break

        all_raw_pages.append(page_data)
        save_raw_pages(all_raw_pages, suffix="_INPROGRESS")  # checkpoint every page

        time.sleep(REQUEST_DELAY_SECONDS)

    return all_raw_pages


def pages_to_dataframe(all_raw_pages: list[dict]) -> pd.DataFrame:
    records = []
    for page_data in all_raw_pages:
        for appid_str, app_info in page_data.items():
            records.append(app_info)
    return pd.DataFrame(records)


def main():
    print("Fetching full app list from SteamSpy (this will take a while — 1 page/minute)...")
    all_raw_pages = fetch_all_pages()

    saved_path = save_raw_pages(all_raw_pages)  # final clean save
    print(f"Raw JSON saved to: {saved_path}")

    df = pages_to_dataframe(all_raw_pages)
    print(f"Total apps returned: {len(df):,}")
    print(df[["appid", "name", "positive", "negative"]].head())

    return df


if __name__ == "__main__":
    main()