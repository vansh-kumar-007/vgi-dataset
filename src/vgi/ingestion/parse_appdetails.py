"""
Parses a single raw Steam appdetails response into validated rows
for every table in our schema (games, developers, genres, screenshots, etc).

Handles the real-world messiness we've already observed:
- Not every field is present on every game.
- release_date can be a real date OR a "coming soon" text flag.
- developers/publishers have no Steam-assigned ID -> uses EntityRegistry.
- achievements are a partial "highlighted" subset, not exhaustive (documented).
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))  # project root
from src.vgi.validation.schemas import (
    Game, Developer, Publisher, GameDeveloper, GamePublisher,
    Genre, GameGenre, Category, GameCategory,
    Screenshot, Trailer, Achievement, GameDLC, ContentRating,
)
from src.vgi.resolution.entity_registry import EntityRegistry


def parse_release_date(release_date_field: Optional[dict]) -> tuple[Optional[str], bool]:
    """Returns (iso_date_string_or_None, is_unreleased_flag)."""
    if not release_date_field:
        return None, False

    coming_soon = release_date_field.get("coming_soon", False)
    date_str = release_date_field.get("date", "")

    if coming_soon or not date_str:
        return None, True

    try:
        parsed = datetime.strptime(date_str, "%d %b, %Y").date()
        return parsed.isoformat(), False
    except ValueError:
        # Steam's date formats aren't always consistent (e.g. month-year only)
        return None, True


class AppDetailsParser:
    def __init__(self, dev_registry: EntityRegistry, pub_registry: EntityRegistry):
        self.dev_registry = dev_registry
        self.pub_registry = pub_registry

    def parse(self, game_id: str, raw: dict) -> dict:
        """
        Parses one game's raw appdetails 'data' payload.
        Returns a dict of lists, one key per table, e.g. {'games': [...], 'genres': [...]}.
        """
        out = {
            "games": [], "developers": [], "publishers": [],
            "game_developers": [], "game_publishers": [],
            "genres": [], "game_genres": [],
            "categories": [], "game_categories": [],
            "screenshots": [], "trailers": [], "achievements": [],
            "dlc": [], "content_ratings": [],
        }

        steam_appid = raw.get("steam_appid")
        release_date_iso, is_unreleased = parse_release_date(raw.get("release_date"))
        platforms = raw.get("platforms", {})

        out["games"].append(Game(
            game_id=game_id,
            steam_appid=steam_appid,
            name=raw.get("name", ""),
            type=raw.get("type", "unknown"),
            is_free=raw.get("is_free", False),
            required_age=int(raw.get("required_age", 0) or 0),
            short_description=raw.get("short_description"),
            detailed_description=raw.get("detailed_description"),
            release_date=release_date_iso,
            release_date_unreleased=is_unreleased,
            header_image_url=raw.get("header_image"),
            supports_windows=platforms.get("windows", False),
            supports_mac=platforms.get("mac", False),
            supports_linux=platforms.get("linux", False),
        ).model_dump())

        for dev_name in raw.get("developers", []) or []:
            dev_id = self.dev_registry.get_or_create_id(dev_name)
            out["developers"].append(Developer(developer_id=dev_id, name=dev_name.strip()).model_dump())
            out["game_developers"].append(GameDeveloper(game_id=game_id, developer_id=dev_id).model_dump())

        for pub_name in raw.get("publishers", []) or []:
            pub_id = self.pub_registry.get_or_create_id(pub_name)
            out["publishers"].append(Publisher(publisher_id=pub_id, name=pub_name.strip()).model_dump())
            out["game_publishers"].append(GamePublisher(game_id=game_id, publisher_id=pub_id).model_dump())

        for genre in raw.get("genres", []) or []:
            gid = str(genre.get("id"))
            out["genres"].append(Genre(genre_id=gid, name=genre.get("description", "")).model_dump())
            out["game_genres"].append(GameGenre(game_id=game_id, genre_id=gid).model_dump())

        for cat in raw.get("categories", []) or []:
            cid = str(cat.get("id"))
            out["categories"].append(Category(category_id=cid, name=cat.get("description", "")).model_dump())
            out["game_categories"].append(GameCategory(game_id=game_id, category_id=cid).model_dump())

        for shot in raw.get("screenshots", []) or []:
            out["screenshots"].append(Screenshot(
                game_id=game_id,
                screenshot_id=str(shot.get("id")),
                thumbnail_url=shot.get("path_thumbnail", ""),
                full_url=shot.get("path_full", ""),
            ).model_dump())

        for movie in raw.get("movies", []) or []:
            webm = (movie.get("webm") or {}).get("max")
            mp4 = (movie.get("mp4") or {}).get("max")
            out["trailers"].append(Trailer(
                game_id=game_id,
                trailer_id=str(movie.get("id")),
                name=movie.get("name", ""),
                thumbnail_url=movie.get("thumbnail"),
                webm_url=webm,
                mp4_url=mp4,
            ).model_dump())

        # NOTE: 'highlighted' is a partial subset per achievements limitation, documented separately.
        achievements_field = raw.get("achievements", {}) or {}
        for ach in achievements_field.get("highlighted", []) or []:
            out["achievements"].append(Achievement(
                game_id=game_id,
                achievement_name=ach.get("name", ""),
                description=None,  # Storefront's 'highlighted' list omits descriptions
                icon_url=ach.get("path"),
                hidden=False,
            ).model_dump())

        for dlc_appid in raw.get("dlc", []) or []:
            out["dlc"].append(GameDLC(game_id=game_id, dlc_steam_appid=dlc_appid).model_dump())

        ratings = raw.get("ratings", {}) or {}
        for board, info in ratings.items():
            if isinstance(info, dict) and info.get("rating"):
                out["content_ratings"].append(ContentRating(
                    game_id=game_id,
                    rating_board=board,
                    rating_value=info.get("rating"),
                    descriptors=info.get("descriptors"),
                ).model_dump())

        return out