"""
Exports all processed Parquet tables to CSV for Kaggle publishing.
CSV is the primary/most-accessible format for Kaggle users; Parquet
remains available in the same output folder for users who prefer it.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

TABLES = [
    "games", "developers", "publishers", "game_developers", "game_publishers",
    "genres", "game_genres", "categories", "game_categories",
    "screenshots", "trailers", "achievements", "dlc", "content_ratings",
]


def main():
    print("Exporting processed tables to CSV...\n")
    for table in TABLES:
        parquet_path = PROCESSED_DIR / f"{table}.parquet"
        csv_path = PROCESSED_DIR / f"{table}.csv"

        df = pd.read_parquet(parquet_path)
        df.to_csv(csv_path, index=False)

        size_mb = csv_path.stat().st_size / (1024 * 1024)
        print(f"  {table}: {len(df):,} rows -> {csv_path.name} ({size_mb:.2f} MB)")

    print("\nDone. Both CSV and Parquet versions now available in data/processed/.")


if __name__ == "__main__":
    main()