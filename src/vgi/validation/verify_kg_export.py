import pandas as pd

nodes = pd.read_parquet("data/processed/kg_nodes.parquet")
edges = pd.read_parquet("data/processed/kg_edges.parquet")

print(f"Total nodes: {len(nodes):,}")
print(f"Duplicate node ids: {nodes['id'].duplicated().sum()}")
print(f"Total edges: {len(edges):,}")

node_ids = set(nodes["id"])
orphan_sources = ~edges["source"].isin(node_ids)
orphan_targets = ~edges["target"].isin(node_ids)

print(f"Edges with unknown source node: {orphan_sources.sum()}")
print(f"Edges with unknown target node: {orphan_targets.sum()}")

print(f"\nDuplicate edges (same source/target/relation): {edges.duplicated().sum()}")

print("\n--- Duplicate node ID details ---")
dupe_ids = nodes[nodes["id"].duplicated(keep=False)].sort_values("id")
print(dupe_ids.head(20))

print("\n--- Duplicate edge details ---")
dupe_edges = edges[edges.duplicated(keep=False)].sort_values(["source", "target", "relation"])
print(dupe_edges.head(10))