"""
Pydantic schemas defining the shape of every core table in the VGI Dataset.
These are the single source of truth for field names/types across the project.
Ingestion scripts validate raw API data against these before it's considered
"clean" and saved to data/processed/.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Game(BaseModel):
    """Core entity table — one row per game."""
    game_id: str  # our internal crosswalk ID, assigned at ingestion time
    steam_appid: int
    name: str
    type: str  # "game", "dlc", "demo", etc.
    is_free: bool
    required_age: int = 0
    short_description: Optional[str] = None
    detailed_description: Optional[str] = None
    release_date: Optional[date] = None
    release_date_unreleased: bool = False  # Steam sometimes gives a text flag instead of a date
    header_image_url: Optional[str] = None
    supports_windows: bool = False
    supports_mac: bool = False
    supports_linux: bool = False


class Developer(BaseModel):
    developer_id: str
    name: str


class Publisher(BaseModel):
    publisher_id: str
    name: str


class GameDeveloper(BaseModel):
    """Junction table: many-to-many games <-> developers."""
    game_id: str
    developer_id: str


class GamePublisher(BaseModel):
    """Junction table: many-to-many games <-> publishers."""
    game_id: str
    publisher_id: str


class Genre(BaseModel):
    genre_id: str  # Steam's own genre id, reused directly
    name: str


class GameGenre(BaseModel):
    game_id: str
    genre_id: str


class Category(BaseModel):
    category_id: str
    name: str


class GameCategory(BaseModel):
    game_id: str
    category_id: str


class Screenshot(BaseModel):
    """Reference-only: URL, never the image itself (per LICENSE_POLICY.md)."""
    game_id: str
    screenshot_id: str
    thumbnail_url: str
    full_url: str


class Trailer(BaseModel):
    """Reference-only: URL, never the video itself."""
    game_id: str
    trailer_id: str
    name: str
    thumbnail_url: Optional[str] = None
    webm_url: Optional[str] = None
    mp4_url: Optional[str] = None


class Achievement(BaseModel):
    game_id: str
    achievement_name: str
    description: Optional[str] = None
    icon_url: Optional[str] = None
    hidden: bool = False


class GameDLC(BaseModel):
    """Self-referencing: links a base game to its DLC appids."""
    game_id: str
    dlc_steam_appid: int


class ContentRating(BaseModel):
    game_id: str
    rating_board: str  # e.g. "esrb", "pegi", "usk"
    rating_value: Optional[str] = None
    descriptors: Optional[str] = None  # comma-joined content descriptors