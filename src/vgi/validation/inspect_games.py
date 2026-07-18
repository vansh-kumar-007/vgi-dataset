"""
Data quality inspection of the core games table — actually looking at
the content, not just row counts and parse-success mechanics.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    df = pd.read_parquet(PROCESSED_DIR / "games.parquet")

    print(f"Total games: {len(df):,}\n")

    print("--- Null counts per column ---")
    print(df.isna().sum().sort_values(ascending=False))

    print("\n--- Duplicate steam_appid check ---")
    print(f"Duplicates: {df['steam_appid'].duplicated().sum()}")

    print("\n--- Duplicate game_id check ---")
    print(f"Duplicates: {df['game_id'].duplicated().sum()}")

    print("\n--- 'type' value counts (should mostly be 'game') ---")
    print(df["type"].value_counts())

    print("\n--- Games with empty/very short names ---")
    short_names = df[df["name"].str.len() < 2]
    print(f"Count: {len(short_names)}")
    print(short_names[["steam_appid", "name"]].head(10))

    print("\n--- required_age distribution (sanity check for garbage values) ---")
    print(df["required_age"].value_counts().sort_index())

    print("\n--- release_date_unreleased count ---")
    print(df["release_date_unreleased"].value_counts())

    print("\n--- Platform support distribution ---")
    print(f"Windows: {df['supports_windows'].sum():,}")
    print(f"Mac: {df['supports_mac'].sum():,}")
    print(f"Linux: {df['supports_linux'].sum():,}")

    print("\n--- short_description length distribution ---")
    desc_lens = df["short_description"].dropna().str.len()
    print(desc_lens.describe())


if __name__ == "__main__":
    main()