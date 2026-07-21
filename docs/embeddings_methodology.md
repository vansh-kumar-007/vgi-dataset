# Embeddings Methodology

## Model
`sentence-transformers/all-MiniLM-L6-v2` — a compact (384-dimension), fully open,
free, locally-runnable sentence embedding model. Chosen specifically to keep this
dataset's entire pipeline reproducible without any API key or cost, consistent
with this project's approach throughout.

## What's embedded
For each game: `"{name}. Genres: {genres}. Features: {categories}. {short_description}"`
(HTML-stripped). This combines structured taxonomy (genres/categories) with the
game's own short description text into one embedding per game.

## Storage format
**Parquet only, not CSV.** 384-dimensional float vectors as CSV would produce a
very large, entirely unreadable file with no practical benefit — no one manually
inspects a table of raw floating-point numbers. Parquet's columnar compression
handles this data shape far more efficiently, and every practical tool for using
these embeddings (pandas, numpy, FAISS) reads Parquet natively.

## Important property: pre-normalized vectors
All vectors have L2 norm exactly 1.0 (`all-MiniLM-L6-v2`'s native output is
pre-normalized). This means cosine similarity can be computed directly via dot
product — no additional normalization step is needed before building a FAISS
index or computing similarity.

## What is NOT published
A prebuilt vector index (e.g. a FAISS index file) is deliberately not included.
FAISS index binaries are tied to specific library versions and can silently
fail to load correctly across different environments/versions — a real
reproducibility risk. Building an index from these raw embeddings takes only
seconds (demonstrated in the accompanying RAG chatbot notebook), so publishing
portable raw vectors and letting users build their own index is safer and more
broadly compatible.

## Validation
22,912 embeddings generated, zero nulls, zero duplicate game_ids, 100% matched
to the published `games` table, all vectors confirmed unit-normalized.