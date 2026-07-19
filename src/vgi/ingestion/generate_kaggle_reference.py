"""
Generates a clean, copy-paste-ready reference document listing every
file description and column description for manual entry into Kaggle's
UI (workaround for the known version-update metadata bug).
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT
from src.vgi.ingestion.build_kaggle_metadata import COLUMN_DESCRIPTIONS, TABLE_DESCRIPTIONS, TABLE_COLUMN_OVERRIDES

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    lines = ["# Kaggle Manual Entry Reference\n", "Copy-paste these into each file's Edit panel on Kaggle.\n"]

    for table, table_desc in TABLE_DESCRIPTIONS.items():
        df = pd.read_parquet(PROCESSED_DIR / f"{table}.parquet")
        lines.append(f"\n## {table}.csv\n")
        lines.append(f"**File description:**\n{table_desc}\n")
        lines.append("**Column descriptions (in order):**\n")
        overrides = TABLE_COLUMN_OVERRIDES.get(table, {})
        for col in df.columns:
            desc = overrides.get(col) or COLUMN_DESCRIPTIONS.get(col, f"See table description for context on '{col}'.")
            lines.append(f"- `{col}`: {desc}")

    out_path = PROJECT_ROOT / "docs" / "kaggle_manual_entry_reference.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reference written to {out_path}")
    print(f"Total files: {len(TABLE_DESCRIPTIONS)}")


if __name__ == "__main__":
    main()