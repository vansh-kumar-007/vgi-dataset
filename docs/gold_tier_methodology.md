# Gold-Tier Selection Methodology

## Decision
Games qualify for Gold tier if they have **≥ 100 total Steam reviews**
(positive + negative, as reported by SteamSpy).

## Why review count, not another signal
- Review count is available for effectively every real Steam game — unlike,
  say, Metacritic scores, which only cover a minority of titles and would
  systematically exclude indie games (a bias we specifically wanted to avoid
  in a dataset meant to represent the platform broadly).
- It correlates strongly with "this game had genuine, verified players" —
  junk/asset-flip listings on Steam almost universally have 0-10 reviews.

## Why 100 specifically, chosen empirically (not guessed in advance)
Distribution across our full candidate pool (82,521 SteamSpy-listed apps,
pulled 2026-07-18):

| Threshold | Resulting games |
|---|---|
| >= 10 | 56,389 |
| >= 25 | 40,745 |
| >= 50 | 30,661 |
| **>= 100** | **23,066** |
| >= 200 | 17,062 |
| >= 500 | 10,871 |

We targeted our Phase 0 scope goal of 15,000-40,000 Gold-tier games.
100 was chosen over lower thresholds (50, 25) because a higher floor more
reliably filters out shovelware while still landing comfortably within
target range, prioritizing signal quality over raw volume.

## Known limitation
This filter is applied against 82,521 of an estimated larger SteamSpy catalog,
due to a partial data pull (see `docs/known_gaps.md`). Re-verification against
full coverage is planned before Silver-tier scoping.

## Reproducibility
This threshold is centrally defined in `config/settings.py` as
`GOLD_MIN_STEAM_REVIEWS`, and applied via `src/vgi/ingestion/build_gold_candidates.py`.
Changing the threshold and rerunning that script regenerates the candidate list.