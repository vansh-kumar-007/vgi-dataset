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
                parsed = parser.parse(game_id=game_id, raw=record["data"])
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

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    print("\nSaving processed tables:")
    for table, rows in accumulated.items():
        df = pd.DataFrame(rows)
        out_path = PROCESSED_DIR / f"{table}.parquet"
        df.to_parquet(out_path, index=False)
        print(f"  {table}: {len(df):,} rows -> {out_path.name}")


if __name__ == "__main__":
    main()