"""
Merges SteamSpy review/owner/price data into the published games table.
Adds regression/classification-ready target variables:
  - review_score (0-1, for rating regression)
  - owners_min / owners_max (for commercial success classification)
  - price_usd (bonus, cleaned numeric price)

This is a point-in-time snapshot, not a time series — documented explicitly
as a known scope limitation, distinct from the deferred Price Prediction
(time series) notebook which needs a proper historical price source.
"""

import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"


def parse_owners_range(owners_str: str) -> tuple[float, float]:
    """Parses SteamSpy's '1,000,000 .. 2,000,000' format into (min, max) floats."""
    if not isinstance(owners_str, str):
        return (None, None)
    parts = re.findall(r"[\d,]+", owners_str)
    if len(parts) != 2:
        return (None, None)
    low = float(parts[0].replace(",", ""))
    high = float(parts[1].replace(",", ""))
    return (low, high)


def main():
    games = pd.read_parquet(PROCESSED_DIR / "games.parquet")
    steamspy = pd.read_parquet(INTERIM_DIR / "steamspy_apps_raw.parquet")

    print(f"Games (published): {len(games):,}")
    print(f"SteamSpy source rows: {len(steamspy):,}")

    steamspy_features = steamspy[["appid", "positive", "negative", "owners", "price"]].copy()
    steamspy_features = steamspy_features.rename(columns={
        "positive": "positive_reviews",
        "negative": "negative_reviews",
        "appid": "steam_appid",
    })

    owners_parsed = steamspy_features["owners"].apply(parse_owners_range)
    steamspy_features["owners_min"] = owners_parsed.apply(lambda t: t[0])
    steamspy_features["owners_max"] = owners_parsed.apply(lambda t: t[1])
    steamspy_features = steamspy_features.drop(columns=["owners"])

    # Price is stored as a string of cents (e.g. "2099" = $20.99); "0" = free
    steamspy_features["price_usd"] = pd.to_numeric(steamspy_features["price"], errors="coerce") / 100
    steamspy_features = steamspy_features.drop(columns=["price"])

    merged = games.merge(steamspy_features, on="steam_appid", how="left")

    total_reviews = merged["positive_reviews"] + merged["negative_reviews"]
    merged["review_score"] = (merged["positive_reviews"] / total_reviews).where(total_reviews > 0)

    matched = merged["positive_reviews"].notna().sum()
    print(f"\nGames successfully matched to SteamSpy features: {matched:,} / {len(merged):,}")
    print(f"Games with unmatched (null) SteamSpy features: {len(merged) - matched:,}")

    print("\nSample of new columns:")
    print(merged[["name", "positive_reviews", "negative_reviews", "review_score", "owners_min", "owners_max", "price_usd"]].head())

    out_path = PROCESSED_DIR / "games.parquet"
    merged.to_parquet(out_path, index=False)
    print(f"\nUpdated games.parquet saved to {out_path}")


if __name__ == "__main__":
    main()