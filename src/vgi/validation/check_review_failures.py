import json
import pandas as pd

records = [
    json.loads(line)
    for line in open(
        "data/raw/steam/review_summaries_all.jsonl",
        encoding="utf-8"
    )
]

print(f"Total records: {len(records)}")

failed = [r for r in records if not r["success"]]
print(f"Failed: {len(failed)}")

desc_counts = pd.Series(
    r["summary"]["review_score_desc"]
    for r in records
    if r["success"]
).value_counts()

print(desc_counts)