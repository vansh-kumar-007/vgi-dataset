# Known Data Gaps

## SteamSpy `all` endpoint — partial pull (2026-07-18)

**What happened:** SteamSpy's bulk `all` listing endpoint became unreliable starting
at page 87 (server returned "Connection failed: Too many connections" and later
HTTP 500 errors consistently, not intermittently). This appears to be a server-side
issue on SteamSpy's end, not a client-side rate-limit violation (we were respecting
their documented 1 request/minute limit for this endpoint).

**Coverage captured:** Pages 0–86, sorted by SteamSpy's default ordering
(descending owner count).
- Raw apps returned: 86,544
- Duplicate appids removed: 4,023 (caused by rankings shifting slightly between
  two separate pull sessions hours apart — same appid landed on different page
  numbers across sessions)
- Final clean unique apps: 82,521

**Impact assessment:** Since Gold-tier selection filters on review count, and
higher-owner-count games strongly correlate with higher review counts (SteamSpy's
own sort order is owner-count descending), this gap is expected to have minimal
impact on Gold-tier composition. The missing pages would represent lower-owner-count,
longer-tail titles — most of which would fail the Gold-tier review threshold anyway.
82,521 candidates is already well above our Gold-tier target range of 15,000–40,000
final games.

**Status:** Deferred, not blocking. To be revisited either as a manual retry once
SteamSpy's server stabilizes, or as part of Phase 12 automation (scheduled
incremental pulls). Will be explicitly re-verified before Silver-tier scoping,
since Silver casts a wider net where this gap could matter more.

## Steam appdetails enrichment — final results (2026-07-18/19)

**Source:** Steam Storefront `appdetails` endpoint (keyless), applied to all
23,066 Gold-tier candidates identified via the SteamSpy review-count filter.

**Result:** 22,918 games successfully enriched (99.36%). 148 failures, all
`success=false` responses from Steam itself — these represent delisted,
region-locked, or removed-from-sale titles that still had a shell listing
in SteamSpy's data but no longer have retrievable store data. This is
expected, benign behavior, not a pipeline defect.

**Method:** Batched ingestion (8 batches of up to 3,000 games), fully
checkpointed via JSONL append-per-record, resumable after any interruption.
Zero parsing errors across all 22,918 successful records when run through
our pydantic-validated parser.

**What this means for the dataset:** our Gold-tier `games` table contains
22,918 rows — slightly below our original 23,066-candidate list, but the
gap is fully explained, expected, and documented, not a silent hole.

## Price/free-status snapshot discrepancy (SteamSpy merge, 2026-07-19)

**What happened:** `is_free` (from Steam's appdetails, Phase 2) and `price_usd` (from SteamSpy, merged later) can disagree for 1,311 games — `is_free=False` while `price_usd=0`. Spot-checking confirms this reflects genuine snapshot timing differences, not a data error: e.g. *Rocket League* and *Fall Guys* both launched as paid games and later became permanently free-to-play, so which field reflects "current" status depends on when each source's snapshot was taken.

**Guidance for users:** `is_free` and `price_usd` are each internally consistent with their own source and collection time, but should not be assumed to represent the exact same moment. For most reliable free/paid classification, `is_free` is the more current signal since it was collected in the same pass as the rest of the `games` table's core fields.

## SteamSpy vs. Valve review count discrepancy (2026-07-19)

**What we found:** Comparing SteamSpy's review counts (collected Phase 2) against
Valve's own official review summary (collected Phase 4) for the same 22,912 games:
- Valve's total is higher for 20,561 games (90%), matches exactly for 574, and is
  lower for 1,777.
- Median difference is small (28 reviews) — consistent with ordinary snapshot-timing
  drift between two collection passes on different dates.
- A minority of games show large gaps (e.g. Call of Duty: Black Ops III: -56,017;
  Starbound: -41,827) — Valve's count meaningfully lower than SteamSpy's for these.

**Root cause: not conclusively determined.** We tested and ruled out one hypothesis
(that our `filter=recent` request parameter caused an undercounted total) — Valve's
own API documentation states `total_reviews` reflects all reviews matching the
query parameters (which we set to `review_type=all`, `purchase_type=all`), not a
recency-limited subset. The most plausible remaining explanation is that our two
sources were collected on different dates, and SteamSpy — a third-party aggregator —
may itself lag behind Steam's live totals with its own update cadence, but this is
not independently confirmed.

**Guidance for users:** for the most current review data, `valve_total_reviews`
and `valve_review_score_desc` (official, first-party) should be treated as more
authoritative than `positive_reviews`/`negative_reviews` (SteamSpy-derived,
third-party). Both are retained for transparency and cross-validation purposes.