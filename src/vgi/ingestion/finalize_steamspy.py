"""
One-off finalization script: converts the SteamSpy checkpoint into
our official raw JSON + interim Parquet artifacts, with basic quality checks
and cleanup (dtype normalization, deduplication).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT
from steam import load_checkpoint, save_raw_pages, pages_to_dataframe


def main():
    pages = load_checkpoint()
    save_raw_pages(pages)

    df = pages_to_dataframe(pages)
    print(f"Total apps (raw, before cleanup): {len(df):,}")

    # --- Fix 1: normalize score_rank (mixed empty-string/int -> proper numeric/NaN) ---
    df["score_rank"] = pd.to_numeric(df["score_rank"], errors="coerce")

    # --- Fix 2: deduplicate on appid (keep first occurrence) ---
    duplicate_count = df["appid"].duplicated().sum()
    print(f"Duplicate appids found: {duplicate_count}")
    df = df.drop_duplicates(subset="appid", keep="first").reset_index(drop=True)
    print(f"Total apps (after deduplication): {len(df):,}")

    null_names = df["name"].isna().sum()
    print(f"Null names: {null_names}")

    interim_dir = PROJECT_ROOT / "data" / "interim"
    interim_dir.mkdir(parents=True, exist_ok=True)
    out_path = interim_dir / "steamspy_apps_raw.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()