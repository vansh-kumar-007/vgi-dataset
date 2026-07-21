"""
Generates production embeddings for all Gold-tier games using
sentence-transformers (all-MiniLM-L6-v2), published as a permanent
dataset artifact (embeddings.parquet).

Deliberately Parquet-only (not CSV) — 384-dimensional float vectors
as CSV would bloat enormously with no real readability benefit.
"""

import re
import sys
from pathlib import Path

import pandas as pd
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def clean_html(text):
    if pd.isna(text):
        return ""
    return re.sub(r"<[^>]+>", " ", text)


def main():
    games = pd.read_parquet(PROCESSED_DIR / "games.parquet")
    genres = pd.read_parquet(PROCESSED_DIR / "genres.parquet")
    game_genres = pd.read_parquet(PROCESSED_DIR / "game_genres.parquet")
    categories = pd.read_parquet(PROCESSED_DIR / "categories.parquet")
    game_categories = pd.read_parquet(PROCESSED_DIR / "game_categories.parquet")

    genre_text = (
        game_genres.merge(genres, on="genre_id")
        .groupby("game_id")["name"].apply(lambda names: ", ".join(names)).rename("genre_text")
    )
    category_text = (
        game_categories.merge(categories, on="category_id")
        .groupby("game_id")["name"].apply(lambda names: ", ".join(names)).rename("category_text")
    )

    games = games.merge(genre_text, on="game_id", how="left")
    games = games.merge(category_text, on="game_id", how="left")
    games["genre_text"] = games["genre_text"].fillna("")
    games["category_text"] = games["category_text"].fillna("")
    games["desc_clean"] = games["short_description"].apply(clean_html)

    games["embedding_text"] = (
        games["name"] + ". Genres: " + games["genre_text"]
        + ". Features: " + games["category_text"]
        + ". " + games["desc_clean"]
    )

    print(f"Generating embeddings for {len(games):,} games...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(
        games["embedding_text"].tolist(),
        show_progress_bar=True,
        batch_size=64,
    )
    print(f"Embeddings shape: {embeddings.shape}")

    embedding_cols = [f"emb_{i}" for i in range(embeddings.shape[1])]
    emb_df = pd.DataFrame(embeddings, columns=embedding_cols)
    emb_df.insert(0, "game_id", games["game_id"].values)

    out_path = PROCESSED_DIR / "embeddings.parquet"
    emb_df.to_parquet(out_path, index=False)
    print(f"Saved to {out_path}")
    print(f"File size: {out_path.stat().st_size / (1024*1024):.2f} MB")


if __name__ == "__main__":
    main()