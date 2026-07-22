# Knowledge Graph Export

## Format
Two flat files: `kg_nodes` and `kg_edges` (CSV + Parquet), the standard
portable format for bulk-loading into Neo4j, Gephi, or any graph library.

## Nodes (48,344 total)
| Type | Count |
|---|---|
| game | 22,912 |
| developer | 14,842 |
| publisher | 10,497 |
| category | 65 |
| genre | 28 |

Columns: `id`, `label`, `type`.

**ID namespacing:** genre and category node IDs are prefixed (`genre_1`, `cat_1`)
to avoid collisions — Steam assigns genres and categories independent ID
sequences, so unprefixed IDs would silently collide (e.g. genre ID 1 = "Action",
category ID 1 = "Multi-player" are different entities that would otherwise share
the same node ID). Games, developers, and publishers already carry unique
internal IDs from the base dataset and did not need prefixing.

## Edges (263,422 total)
| Relation | Count | Direction |
|---|---|---|
| has_category | 147,785 | game → category |
| has_genre | 65,436 | game → genre |
| developed_by | 25,438 | game → developer |
| published_by | 24,763 | game → publisher |

All edges are directed, sourced from the game node. Columns: `source`, `target`, `relation`.

## Data quality note
During export validation, 5 exact duplicate rows were discovered and removed
from the underlying `game_developers` table (a genuine small Phase 2 data gap,
not an export-layer artifact) — `game_developers.csv`/`.parquet` were corrected
at the source as part of this work. Full referential integrity verified:
zero orphaned edges, zero duplicate node IDs, zero duplicate edges.

## Difference from the exploratory KG notebook
The published notebook builds an *undirected*, in-memory graph for exploration
(no categories included). This export is *directed*, includes categories as a
node type, and is published as permanent standalone files rather than
notebook-only code — intended for users who want the graph structure itself,
not just the notebook's specific analysis.