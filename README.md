# The Ultimate Video Game Intelligence Dataset — Gold Tier

A high-quality, relational, multi-table dataset covering **22,912 curated Steam games**, built for machine learning, deep learning, recommendation systems, RAG, knowledge graphs, NLP, and general game-industry analytics.

This is **not a single CSV**. It is a normalized, relational dataset spanning 14 interconnected tables — games, developers, publishers, genres, categories, screenshots, trailers, achievements, DLC relationships, and content ratings — designed the way a real production database would be.

## Why "Gold Tier"?

This is the first of a planned multi-tier release. Rather than scraping every Steam listing indiscriminately (including shovelware, asset flips, and abandoned listings), Gold Tier applies a deliberate, evidence-based quality filter: **every game has at least 100 total Steam reviews**, a threshold chosen empirically (see Methodology below) to balance genuine breadth with data quality. Silver and Bronze tiers (broader coverage, lighter enrichment) are planned as future releases.

## Tables

| Table | Rows | Description |
|---|---|---|
| `games` | 22,912 | Core entity table — one row per game |
| `developers` | 14,842 | Unique developer studios |
| `publishers` | 10,497 | Unique publishers |
| `game_developers` | 25,443 | Many-to-many: games ↔ developers |
| `game_publishers` | 24,763 | Many-to-many: games ↔ publishers |
| `genres` | 28 | Steam's genre taxonomy |
| `game_genres` | 65,436 | Many-to-many: games ↔ genres |
| `categories` | 65 | Steam's feature/category taxonomy (e.g. "Single-player", "Steam Achievements") |
| `game_categories` | 147,785 | Many-to-many: games ↔ categories |
| `screenshots` | 243,512 | Screenshot URLs (reference only, not hosted images) |
| `trailers` | 41,618 | Trailer/movie URLs (reference only) |
| `achievements` | 160,375 | Featured achievements per game (see limitation below) |
| `dlc` | 42,729 | Base game → DLC appid relationships |
| `content_ratings` | 76,125 | Regional content rating board classifications (ESRB/PEGI/etc.) |

Both CSV and Parquet versions of every table are provided.

## Schema — `games` (core table)

| Column | Type | Description |
|---|---|---|
| `game_id` | string | Internal stable identifier (primary key across all tables) |
| `steam_appid` | int | Steam's own App ID |
| `name` | string | Game title |
| `type` | string | Always "game" in this release (demos/other types filtered out) |
| `is_free` | bool | Whether the game is free-to-play |
| `required_age` | int | Age rating requirement, if any |
| `short_description` | string | Steam's short store description |
| `detailed_description` | string | Full store description (contains embedded HTML — see Known Limitations) |
| `release_date` | date (nullable) | Release date, if known |
| `release_date_unreleased` | bool | True if the game was unreleased/had no parseable date at collection time |
| `header_image_url` | string (nullable) | Store header image URL |
| `supports_windows` / `supports_mac` / `supports_linux` | bool | Platform support flags |

Other tables follow standard relational conventions — junction tables use `game_id` + the related entity's own ID; see each CSV's header row for exact columns.

## Methodology

### Sourcing
1. **SteamSpy** (`steamspy.com`) provided the candidate universe of Steam apps, including review counts used for filtering.
2. **Steam Storefront `appdetails`** (unofficial, keyless) provided all enrichment data: descriptions, genres, developers, publishers, screenshots, trailers, achievements, DLC, and content ratings.

### Gold-tier threshold selection
The ≥100-review threshold was chosen empirically, not guessed in advance. Against a candidate pool of 82,521 SteamSpy-listed apps, review-count thresholds produced the following candidate pool sizes:

| Threshold | Candidate games |
|---|---|
| ≥10 reviews | 56,389 |
| ≥25 reviews | 40,745 |
| ≥50 reviews | 30,661 |
| **≥100 reviews (selected)** | **23,066** |
| ≥200 reviews | 17,062 |
| ≥500 reviews | 10,871 |

100 reviews was selected as the best balance between dataset size and filtering out low-signal/shovelware listings, while avoiding over-reliance on critic-score-based filters (which would have systematically excluded indie titles).

### Enrichment success rate
Of 23,066 Gold-tier candidates, 22,918 (99.36%) were successfully enriched via Steam's appdetails endpoint. A further 6 were removed during quality review (4 demos incorrectly typed, 2 hollow/broken listings with empty names on Steam's own side), leaving **22,912 final games**.

## Known Limitations

**SteamSpy candidate pool is a partial pull.** Our SteamSpy-derived candidate universe (82,521 apps) does not represent SteamSpy's complete catalog — pagination was halted due to server-side instability on SteamSpy's end. Given SteamSpy's default sort (descending owner count), the missing apps are expected to be long-tail, low-visibility titles unlikely to meet the ≥100-review Gold threshold regardless. Impact on Gold-tier composition is expected to be minimal.

**Achievements are a "highlighted" subset, not exhaustive.** Steam's keyless Storefront API only exposes a curated highlight list (typically up to ~10 per game) rather than the complete achievement schema. Full achievement lists require an authenticated Steam Web API key (which itself requires a Steam account with a qualifying purchase) — out of scope for this release. The `achievements` table should be treated as a representative sample, not a complete list, for any given game.

**Descriptions contain raw HTML.** The `detailed_description` field preserves Steam's original HTML formatting (e.g. `<br>`, `<ul>` tags) rather than being pre-cleaned. This is intentional — it preserves full fidelity to the source — but downstream NLP/embedding use cases should strip HTML first.

**148 candidates could not be enriched.** These returned `success: false` from Steam's own API, consistent with delisted, region-restricted, or removed-from-sale titles. They are simply absent from the final tables rather than included with blank data.

## License & Attribution

This dataset is built from publicly accessible Steam and SteamSpy data.
- **Steam Storefront API / SteamSpy**: No official redistribution grant exists, but this is a long-established, widely-used practice in the Kaggle and academic research community.
- **No copyrighted media (screenshots, trailers, box art) is redistributed** — only reference URLs are included, per this project's data ethics policy.
- Users of this dataset should independently review Valve's and SteamSpy's terms of use for their own downstream use cases.

**License: CC BY-NC-SA 4.0** (Attribution-NonCommercial-ShareAlike). This dataset may be used and modified freely for non-commercial purposes (research, education, personal projects, competitions) with attribution, and any derivative datasets must carry the same license terms.

## Citation

If you use this dataset in your work, please cite:
Vansh Kumar. "The Ultimate Video Game Intelligence Dataset — Gold Tier." Kaggle, 2026.

## Version History

- **v1.0.0** (2026-07-19) — Initial Gold Tier release. 22,912 games, 14 relational tables.

## Roadmap

- Silver Tier: broader coverage (~100,000+ games), lighter enrichment depth
- Bronze Tier: maximal coverage (500,000+ target), minimal metadata
- Planned enrichment: pricing history, review sentiment, knowledge graph exports, semantic embeddings
