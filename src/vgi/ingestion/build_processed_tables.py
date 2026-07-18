"""
Reads the accumulated appdetails JSONL (however many batches have been fetched
so far), runs it through our parser, and writes out clean per-table Parquet
files to data/processed/. Safe to re-run after every batch — always rebuilds
from the full JSONL accumulated so far, not incrementally.
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT
from src.vgi.ingestion.parse_appdetails import AppDetailsParser
from src.vgi.resolution.entity_registry import EntityRegistry

RAW_JSONL_PATH = PROJECT_ROOT / "data" / "raw" / "steam" / "appdetails_all.jsonl"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    dev_registry = EntityRegistry(prefix="dev")
    pub_registry = EntityRegistry(prefix="pub")
    parser = AppDetailsParser(dev_registry, pub_registry)

    accumulated = {
        "games": [], "developers": [], "publishers": [],
        "game_developers": [], "game_publishers": [],
        "genres": [], "game_genres": [],
        "categories": [], "game_categories": [],
        "screenshots": [], "trailers": [], "achievements": [],
        "dlc": [], "content_ratings": [],
    }

    parse_errors = []
    game_counter = 0

    with open(RAW_JSONL_PATH, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            if not record["success"]:
                continue

            game_counter += 1
            game_id = f"game_{game_counter:06d}"

            try:
                # Use the appid we actually requested, not data.steam_appid,
                # since Steam sometimes returns a different internal appid
                # for bundle/season/hub listings (confirmed case: appid 901663
                # returns data.steam_appid=8260). Our requested appid is what
                # our Gold-tier selection was based on, so it's the correct key.
                raw_data = dict(record["data"])
                raw_data["steam_appid"] = record["appid"]
                parsed = parser.parse(game_id=game_id, raw=raw_data)
                for table, rows in parsed.items():
                    accumulated[table].extend(rows)
            except Exception as e:
                parse_errors.append({"appid": record["appid"], "error": str(e)})

    print(f"Parsed {game_counter:,} successful raw records.")
    print(f"Parse errors: {len(parse_errors)}")
    if parse_errors:
        print("Sample parse errors:")
        for e in parse_errors[:5]:
            print(f"  appid {e['appid']}: {e['error']}")

    # Deduplicate lookup tables (developers/publishers/genres/categories get
    # re-added once per game that references them — dedupe before saving).
    def dedupe(rows: list[dict], key: str) -> list[dict]:
        seen = {}
        for r in rows:
            seen[r[key]] = r
        return list(seen.values())

    accumulated["developers"] = dedupe(accumulated["developers"], "developer_id")
    accumulated["publishers"] = dedupe(accumulated["publishers"], "publisher_id")
    accumulated["genres"] = dedupe(accumulated["genres"], "genre_id")
    accumulated["categories"] = dedupe(accumulated["categories"], "category_id")
    
    # --- Final quality filtering, based on inspection findings ---
    games_df = pd.DataFrame(accumulated["games"])
    before_count = len(games_df)

    # Exclude non-game types (demos slipped into our "games" set)
    games_df = games_df[games_df["type"] == "game"]

    # Exclude broken/hollow listings (empty name — confirmed genuine Steam data issue)
    games_df = games_df[games_df["name"].str.strip() != ""]

    valid_game_ids = set(games_df["game_id"])
    after_count = len(games_df)
    print(f"\nQuality filtering: {before_count:,} -> {after_count:,} games "
          f"(removed {before_count - after_count}: non-game types + broken listings)")

    accumulated["games"] = games_df.to_dict("records")

    # Tables with a direct game_id column — cascade the game filter to these.
    game_keyed_tables = [
        "game_developers", "game_publishers", "game_genres", "game_categories",
        "screenshots", "trailers", "achievements", "dlc", "content_ratings",
    ]
    for table in game_keyed_tables:
        accumulated[table] = [
            row for row in accumulated[table] if row.get("game_id") in valid_game_ids
        ]

    # Lookup tables (developers/publishers/genres/categories) are keyed by
    # their OWN id, not game_id — rebuild them from only the IDs still
    # referenced by the (now-filtered) junction tables, so we don't keep
    # orphaned lookup rows for entities tied only to removed games.
    remaining_dev_ids = {row["developer_id"] for row in accumulated["game_developers"]}
    remaining_pub_ids = {row["publisher_id"] for row in accumulated["game_publishers"]}
    remaining_genre_ids = {row["genre_id"] for row in accumulated["game_genres"]}
    remaining_cat_ids = {row["category_id"] for row in accumulated["game_categories"]}

    accumulated["developers"] = [r for r in accumulated["developers"] if r["developer_id"] in remaining_dev_ids]
    accumulated["publishers"] = [r for r in accumulated["publishers"] if r["publisher_id"] in remaining_pub_ids]
    accumulated["genres"] = [r for r in accumulated["genres"] if r["genre_id"] in remaining_genre_ids]
    accumulated["categories"] = [r for r in accumulated["categories"] if r["category_id"] in remaining_cat_ids]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("\nSaving processed tables:")
    for table, rows in accumulated.items():
        df = pd.DataFrame(rows)
        out_path = PROCESSED_DIR / f"{table}.parquet"
        df.to_parquet(out_path, index=False)
        print(f"  {table}: {len(df):,} rows -> {out_path.name}")


if __name__ == "__main__":
    main()