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