"""
Filters the full SteamSpy app pool down to Gold-tier candidates,
using the threshold defined centrally in config/settings.py.

Output: data/interim/gold_candidates.parquet
This becomes the input list for per-game appdetails enrichment (next step).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT, GOLD_MIN_STEAM_REVIEWS


def main():
    interim_dir = PROJECT_ROOT / "data" / "interim"
    source_path = interim_dir / "steamspy_apps_raw.parquet"

    df = pd.read_parquet(source_path)
    print(f"Loaded {len(df):,} total apps from {source_path}")

    df["total_reviews"] = df["positive"] + df["negative"]

    gold_df = df[df["total_reviews"] >= GOLD_MIN_STEAM_REVIEWS].copy()
    gold_df = gold_df.sort_values("total_reviews", ascending=False).reset_index(drop=True)

    print(f"Gold-tier candidates (>= {GOLD_MIN_STEAM_REVIEWS} reviews): {len(gold_df):,}")

    out_path = interim_dir / "gold_candidates.parquet"
    gold_df.to_parquet(out_path, index=False)
    print(f"Saved to {out_path}")

    # Quick sanity peek
    print("\nTop 5 by review count:")
    print(gold_df[["appid", "name", "total_reviews"]].head())
    print("\nBottom 5 (right at the threshold boundary):")
    print(gold_df[["appid", "name", "total_reviews"]].tail())


if __name__ == "__main__":
    main()