import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

df = pd.read_parquet(PROJECT_ROOT / "data" / "processed" / "games.parquet")

print("--- Duplicate steam_appid rows (both copies shown) ---")
dupe_appids = df[df["steam_appid"].duplicated(keep=False)].sort_values("steam_appid")
print(dupe_appids[["game_id", "steam_appid", "name"]].head(20))
print(f"\nTotal rows involved in duplicates: {len(dupe_appids)}")
print(f"Unique appids affected: {dupe_appids['steam_appid'].nunique()}")

print("\n--- The two blank-name rows, full detail ---")
blank_names = df[df["name"].str.strip() == ""]
print(blank_names[["game_id", "steam_appid", "name", "short_description"]])

print("\n--- Checking gold_candidates.parquet for duplicate appids (should be 0) ---")
candidates_df = pd.read_parquet(PROJECT_ROOT / "data" / "interim" / "gold_candidates.parquet")
print(f"Total candidate rows: {len(candidates_df):,}")
print(f"Duplicate appids in candidates file: {candidates_df['appid'].duplicated().sum()}")

print("\n--- Checking raw JSONL for duplicate appid 8260 specifically ---")
import json
matches = []
with open(PROJECT_ROOT / "data" / "raw" / "steam" / "appdetails_all.jsonl", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        if record["appid"] == 8260:
            matches.append(record)
print(f"Number of JSONL entries for appid 8260: {len(matches)}")
for m in matches:
    print(f"  success={m['success']}, name={m['data'].get('name') if m['data'] else None}")
    
print("\n--- Tracing the two 'appid 8260' games.parquet rows back to their ORIGINAL requested appids ---")
import json

target_game_ids = {"game_017268", "game_017295"}
game_counter = 0
with open(PROJECT_ROOT / "data" / "raw" / "steam" / "appdetails_all.jsonl", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        if not record["success"]:
            continue
        game_counter += 1
        this_game_id = f"game_{game_counter:06d}"
        if this_game_id in target_game_ids:
            print(f"{this_game_id}: REQUESTED appid={record['appid']}, "
                  f"response data.steam_appid={record['data'].get('steam_appid')}, "
                  f"name={record['data'].get('name')}")
            
print("\n--- Full raw record for the two blank-name appids ---")
target_appids = {1548510, 547010}
with open(PROJECT_ROOT / "data" / "raw" / "steam" / "appdetails_all.jsonl", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        if record["appid"] in target_appids:
            print(f"\nappid {record['appid']}:")
            print(f"  type: {record['data'].get('type')}")
            print(f"  is_free: {record['data'].get('is_free')}")
            print(f"  detailed_description length: {len(record['data'].get('detailed_description', ''))}")
            print(f"  all keys present: {list(record['data'].keys())}")