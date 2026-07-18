import json

records = [json.loads(line) for line in open("data/raw/steam/appdetails_all.jsonl", encoding="utf-8")]
print(f"Total records: {len(records)}")

failed = [r for r in records if not r["success"]]
print(f"Failed: {len(failed)}")

print("\nMost recent 15 failures (from latest batch):")
for f in failed[-15:]:
    print(f"  appid {f['appid']}: {f['error']}")