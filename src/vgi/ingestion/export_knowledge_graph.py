"""
Formal knowledge graph export: nodes.csv/parquet + edges.csv/parquet.
Directed, typed edges — a proper export for use in Neo4j, Gephi, or any
graph library, distinct from the exploratory in-notebook NetworkX demo.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    games = pd.read_parquet(PROCESSED_DIR / "games.parquet")
    developers = pd.read_parquet(PROCESSED_DIR / "developers.parquet")
    publishers = pd.read_parquet(PROCESSED_DIR / "publishers.parquet")
    genres = pd.read_parquet(PROCESSED_DIR / "genres.parquet")
    categories = pd.read_parquet(PROCESSED_DIR / "categories.parquet")
    game_developers = pd.read_parquet(PROCESSED_DIR / "game_developers.parquet")
    game_publishers = pd.read_parquet(PROCESSED_DIR / "game_publishers.parquet")
    game_genres = pd.read_parquet(PROCESSED_DIR / "game_genres.parquet")
    game_categories = pd.read_parquet(PROCESSED_DIR / "game_categories.parquet")

    # --- Nodes: id, label, type ---
    genres_prefixed = genres.copy()
    genres_prefixed["genre_id"] = "genre_" + genres_prefixed["genre_id"].astype(str)
    categories_prefixed = categories.copy()
    categories_prefixed["category_id"] = "cat_" + categories_prefixed["category_id"].astype(str)

    node_frames = [
        games[["game_id", "name"]].rename(columns={"game_id": "id", "name": "label"}).assign(type="game"),
        developers[["developer_id", "name"]].rename(columns={"developer_id": "id", "name": "label"}).assign(type="developer"),
        publishers[["publisher_id", "name"]].rename(columns={"publisher_id": "id", "name": "label"}).assign(type="publisher"),
        genres_prefixed[["genre_id", "name"]].rename(columns={"genre_id": "id", "name": "label"}).assign(type="genre"),
        categories_prefixed[["category_id", "name"]].rename(columns={"category_id": "id", "name": "label"}).assign(type="category"),
    ]
    nodes = pd.concat(node_frames, ignore_index=True)

    # --- Edges: source, target, relation (all directed FROM game TO the related entity) ---
    game_genres_prefixed = game_genres.copy()
    game_genres_prefixed["genre_id"] = "genre_" + game_genres_prefixed["genre_id"].astype(str)
    game_categories_prefixed = game_categories.copy()
    game_categories_prefixed["category_id"] = "cat_" + game_categories_prefixed["category_id"].astype(str)

    edge_frames = [
        game_developers.drop_duplicates().rename(columns={"game_id": "source", "developer_id": "target"}).assign(relation="developed_by"),
        game_publishers.drop_duplicates().rename(columns={"game_id": "source", "publisher_id": "target"}).assign(relation="published_by"),
        game_genres_prefixed.rename(columns={"game_id": "source", "genre_id": "target"}).assign(relation="has_genre"),
        game_categories_prefixed.rename(columns={"game_id": "source", "category_id": "target"}).assign(relation="has_category"),
    ]
    edges = pd.concat([df[["source", "target", "relation"]] for df in edge_frames], ignore_index=True)

    print(f"Nodes: {len(nodes):,}")
    print(nodes["type"].value_counts())
    print(f"\nEdges: {len(edges):,}")
    print(edges["relation"].value_counts())

    # Save both formats
    for fmt in ["csv", "parquet"]:
        nodes_path = PROCESSED_DIR / f"kg_nodes.{fmt}"
        edges_path = PROCESSED_DIR / f"kg_edges.{fmt}"
        if fmt == "csv":
            nodes.to_csv(nodes_path, index=False)
            edges.to_csv(edges_path, index=False)
        else:
            nodes.to_parquet(nodes_path, index=False)
            edges.to_parquet(edges_path, index=False)
        print(f"\nSaved {nodes_path.name}, {edges_path.name}")


if __name__ == "__main__":
    main()