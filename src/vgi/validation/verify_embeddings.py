import pandas as pd
import numpy as np

emb_df = pd.read_parquet("data/processed/embeddings.parquet")
print(f"Shape: {emb_df.shape}")
print(f"Null values: {emb_df.isna().sum().sum()}")
print(f"Duplicate game_ids: {emb_df['game_id'].duplicated().sum()}")

games = pd.read_parquet("data/processed/games.parquet")
matched = emb_df["game_id"].isin(games["game_id"]).sum()
print(f"Matched to games table: {matched:,} / {len(emb_df):,}")

embedding_cols = [c for c in emb_df.columns if c.startswith("emb_")]
vectors = emb_df[embedding_cols].values
norms = np.linalg.norm(vectors, axis=1)
print(f"Vector norm range: {norms.min():.3f} to {norms.max():.3f}")