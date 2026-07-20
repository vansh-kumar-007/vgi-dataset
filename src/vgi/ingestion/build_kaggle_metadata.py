"""
Generates a complete dataset-metadata.json for Kaggle, including
subtitle, full description, and per-file/per-column documentation —
directly improving Kaggle's usability score (Completeness + Compatibility).
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from config.settings import PROJECT_ROOT

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
UPLOAD_DIR = PROJECT_ROOT / "kaggle_upload"

# Column descriptions — reused across tables wherever the same column appears.
COLUMN_DESCRIPTIONS = {
    "game_id": "Internal stable identifier, primary key linking this row to the games table.",
    "steam_appid": "Steam's own App ID for this game.",
    "name": "Game title as listed on Steam.",
    "type": "Steam listing type (always 'game' in this Gold-tier release).",
    "is_free": "Whether the game is free-to-play.",
    "required_age": "Minimum age requirement, if any (0 if none specified).",
    "short_description": "Steam's short store description.",
    "detailed_description": "Full store description. Contains raw embedded HTML formatting.",
    "release_date": "Release date, if known and parseable.",
    "release_date_unreleased": "True if the game was unreleased or had no parseable release date at collection time.",
    "header_image_url": "URL to the game's Steam store header image (reference only, not hosted).",
    "supports_windows": "Whether the game supports Windows.",
    "supports_mac": "Whether the game supports macOS.",
    "supports_linux": "Whether the game supports Linux.",
    "developer_id": "Internal stable identifier for this developer studio.",
    "publisher_id": "Internal stable identifier for this publisher.",
    "genre_id": "Steam's own genre identifier.",
    "category_id": "Steam's own feature/category identifier (e.g. 'Single-player', 'Steam Achievements').",
    "screenshot_id": "Identifier for this screenshot as assigned by Steam.",
    "thumbnail_url": "URL to a thumbnail-sized image (reference only, not hosted).",
    "full_url": "URL to the full-size image (reference only, not hosted).",
    "trailer_id": "Identifier for this trailer/movie as assigned by Steam.",
    "webm_url": "URL to the WebM version of the trailer, if available.",
    "mp4_url": "URL to the MP4 version of the trailer, if available.",
    "achievement_name": "Internal name of the achievement.",
    "description": "Achievement description text, where available.",
    "icon_url": "URL to the achievement's icon image (reference only, not hosted).",
    "hidden": "Whether this achievement is a hidden/secret achievement.",
    "dlc_steam_appid": "Steam App ID of a piece of downloadable content (DLC) for this base game.",
    "rating_board": "Regional content rating board (e.g. 'esrb', 'pegi', 'usk').",
    "rating_value": "The rating value assigned by this board, if available.",
    "descriptors": "Content descriptors associated with this rating (e.g. violence, language).",
    "positive_reviews": "Total positive review count, as reported by SteamSpy.",
    "negative_reviews": "Total negative review count, as reported by SteamSpy.",
    "review_score": "Positive review ratio (positive / total reviews), range 0-1. Useful as a regression target.",
    "owners_min": "Estimated minimum owner count, as reported by SteamSpy (range-based estimate, not exact).",
    "owners_max": "Estimated maximum owner count, as reported by SteamSpy (range-based estimate, not exact).",
    "price_usd": "Price in USD at time of SteamSpy collection. May differ from is_free if the game's pricing changed between data collection passes (see known_gaps.md).",
}

TABLE_DESCRIPTIONS = {
    "games": "Core entity table. One row per game, with title, description, release info, and platform support.",
    "developers": "Unique developer studios referenced across the dataset.",
    "publishers": "Unique publishers referenced across the dataset.",
    "game_developers": "Many-to-many relationship: which developer(s) made which game(s).",
    "game_publishers": "Many-to-many relationship: which publisher(s) released which game(s).",
    "genres": "Steam's genre taxonomy (e.g. Action, RPG, Strategy).",
    "game_genres": "Many-to-many relationship: which genre(s) apply to which game(s).",
    "categories": "Steam's feature/category taxonomy (e.g. Single-player, Steam Achievements, Multiplayer).",
    "game_categories": "Many-to-many relationship: which categories/features apply to which game(s).",
    "screenshots": "Screenshot reference URLs per game (images not hosted, only linked).",
    "trailers": "Trailer/movie reference URLs per game (videos not hosted, only linked).",
    "achievements": "Featured achievements per game, as exposed by Steam's public API (partial subset, not exhaustive).",
    "dlc": "Base game to downloadable content (DLC) relationships.",
    "content_ratings": "Regional content rating board classifications per game (e.g. ESRB, PEGI).",
}

PANDAS_TO_KAGGLE_TYPE = {
    "object": "string",
    "int64": "integer",
    "int32": "integer",
    "float64": "number",
    "bool": "boolean",
    "datetime64[ns]": "datetime",
}


def infer_kaggle_type(dtype) -> str:
    return PANDAS_TO_KAGGLE_TYPE.get(str(dtype), "string")


# Context-sensitive overrides: same column name means different things
# in different tables (e.g. 'name' is a game title in one table, a
# developer studio name in another).
TABLE_COLUMN_OVERRIDES = {
    "developers": {"name": "Developer studio name."},
    "publishers": {"name": "Publisher name."},
    "genres": {"name": "Genre name (e.g. Action, RPG, Strategy)."},
    "categories": {"name": "Category/feature name (e.g. Single-player, Steam Achievements)."},
    "trailers": {"name": "Trailer/movie title as labeled by Steam."},
}


def build_resources():
    resources = []
    for table, table_desc in TABLE_DESCRIPTIONS.items():
        df = pd.read_parquet(PROCESSED_DIR / f"{table}.parquet")
        fields = []
        overrides = TABLE_COLUMN_OVERRIDES.get(table, {})
        for col in df.columns:
            desc = overrides.get(col) or COLUMN_DESCRIPTIONS.get(col, f"See table description for context on '{col}'.")
            fields.append({
                "name": col,
                "title": desc,
                "description": desc,
                "type": infer_kaggle_type(df[col].dtype),
            })
        resources.append({
            "path": f"{table}.csv",
            "description": table_desc,
            "schema": {"fields": fields},
        })
    return resources


def main():
    readme_text = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    metadata = {
        "title": "Ultimate Video Game Intelligence (Gold Tier)",
        "id": "vanshkumar007/ultimate-video-game-intelligence-dataset-gold",
        "subtitle": "22,912 curated Steam games across 14 relational tables for ML and RAG",
        "description": readme_text,
        "licenses": [{"name": "CC-BY-NC-SA-4.0"}],
        "keywords": ["video games", "gaming", "steam", "relational database", "recommender systems"],
        "resources": build_resources(),
    }

    out_path = UPLOAD_DIR / "dataset-metadata.json"
    out_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote metadata to {out_path}")
    print(f"Subtitle length: {len(metadata['subtitle'])} chars (must be 20-80)")
    print(f"Resources documented: {len(metadata['resources'])}")


if __name__ == "__main__":
    main()