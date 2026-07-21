"""
Merges Valve's official review summary data into the published games table.
Handles a real Steam API quirk: games with too few reviews return a literal
"N user reviews" string instead of a category like "Very Positive"/"Mixed" —
these are normalized to a consistent "Too Few Reviews" label.
"""

import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
RAW_JSONL_PATH = PROJECT_ROOT / "data" / "raw" / "steam" / "review_summaries_all.jsonl"

LOW_REVIEW_PATTERN = re.compile(r"^\d+ user reviews?$", re.IGNORECASE)


def normalize_desc(desc: str) -> str:
    if desc == "No user reviews" or LOW_REVIEW_PATTERN.match(desc):
        return "Too Few Reviews"
    return desc


def main():
    games = pd.read_parquet(PROCESSED_DIR / "games.parquet")

    records = []
    with open(RAW_JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            if rec["success"]:
                summary = rec["summary"]
                records.append({
                    "steam_appid": rec["appid"],
                    "valve_review_score_desc": normalize_desc(summary.get("review_score_desc", "")),
                    "valve_total_positive": summary.get("total_positive"),
                    "valve_total_negative": summary.get("total_negative"),
                    "valve_total_reviews": summary.get("total_reviews"),
                })

    valve_df = pd.DataFrame(records)
    print(f"Valve review records: {len(valve_df):,}")
    print("\nNormalized category distribution:")
    print(valve_df["valve_review_score_desc"].value_counts())

    merged = games.merge(valve_df, on="steam_appid", how="left")
    matched = merged["valve_review_score_desc"].notna().sum()
    print(f"\nGames matched: {matched:,} / {len(merged):,}")

    out_path = PROCESSED_DIR / "games.parquet"
    merged.to_parquet(out_path, index=False)
    print(f"\nUpdated games.parquet saved to {out_path}")


if __name__ == "__main__":
    main()