"""
Central configuration for the VGI Dataset project.
Every module should import paths/constants from here — never hardcode them.
"""

from pathlib import Path

# --- Project root (this file lives in config/, so root is one level up) ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Data directories ---
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

# --- Docs ---
DOCS_DIR = PROJECT_ROOT / "docs"

# --- Gold-tier filter (placeholder — will be set empirically in Phase 2) ---
GOLD_MIN_STEAM_REVIEWS = None  # TODO: set after Phase 2 review-count distribution analysis

# --- Steam API ---
STEAM_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"