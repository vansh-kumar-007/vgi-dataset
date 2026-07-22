import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

df = pd.read_parquet(PROCESSED_DIR / "game_developers.parquet")
before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
after = len(df)

print(f"Before: {before:,} rows")
print(f"After: {after:,} rows")
print(f"Removed: {before - after} duplicate rows")

df.to_parquet(PROCESSED_DIR / "game_developers.parquet", index=False)
df.to_csv(PROCESSED_DIR / "game_developers.csv", index=False)
print("Saved cleaned game_developers table (Parquet + CSV).")