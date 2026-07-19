# Kaggle Manual Entry Reference

Copy-paste these into each file's Edit panel on Kaggle.


## games.csv

**File description:**
Core entity table. One row per game, with title, description, release info, and platform support.

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `steam_appid`: Steam's own App ID for this game.
- `name`: Game title as listed on Steam.
- `type`: Steam listing type (always 'game' in this Gold-tier release).
- `is_free`: Whether the game is free-to-play.
- `required_age`: Minimum age requirement, if any (0 if none specified).
- `short_description`: Steam's short store description.
- `detailed_description`: Full store description. Contains raw embedded HTML formatting.
- `release_date`: Release date, if known and parseable.
- `release_date_unreleased`: True if the game was unreleased or had no parseable release date at collection time.
- `header_image_url`: URL to the game's Steam store header image (reference only, not hosted).
- `supports_windows`: Whether the game supports Windows.
- `supports_mac`: Whether the game supports macOS.
- `supports_linux`: Whether the game supports Linux.

## developers.csv

**File description:**
Unique developer studios referenced across the dataset.

**Column descriptions (in order):**

- `developer_id`: Internal stable identifier for this developer studio.
- `name`: Developer studio name.

## publishers.csv

**File description:**
Unique publishers referenced across the dataset.

**Column descriptions (in order):**

- `publisher_id`: Internal stable identifier for this publisher.
- `name`: Publisher name.

## game_developers.csv

**File description:**
Many-to-many relationship: which developer(s) made which game(s).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `developer_id`: Internal stable identifier for this developer studio.

## game_publishers.csv

**File description:**
Many-to-many relationship: which publisher(s) released which game(s).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `publisher_id`: Internal stable identifier for this publisher.

## genres.csv

**File description:**
Steam's genre taxonomy (e.g. Action, RPG, Strategy).

**Column descriptions (in order):**

- `genre_id`: Steam's own genre identifier.
- `name`: Genre name (e.g. Action, RPG, Strategy).

## game_genres.csv

**File description:**
Many-to-many relationship: which genre(s) apply to which game(s).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `genre_id`: Steam's own genre identifier.

## categories.csv

**File description:**
Steam's feature/category taxonomy (e.g. Single-player, Steam Achievements, Multiplayer).

**Column descriptions (in order):**

- `category_id`: Steam's own feature/category identifier (e.g. 'Single-player', 'Steam Achievements').
- `name`: Category/feature name (e.g. Single-player, Steam Achievements).

## game_categories.csv

**File description:**
Many-to-many relationship: which categories/features apply to which game(s).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `category_id`: Steam's own feature/category identifier (e.g. 'Single-player', 'Steam Achievements').

## screenshots.csv

**File description:**
Screenshot reference URLs per game (images not hosted, only linked).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `screenshot_id`: Identifier for this screenshot as assigned by Steam.
- `thumbnail_url`: URL to a thumbnail-sized image (reference only, not hosted).
- `full_url`: URL to the full-size image (reference only, not hosted).

## trailers.csv

**File description:**
Trailer/movie reference URLs per game (videos not hosted, only linked).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `trailer_id`: Identifier for this trailer/movie as assigned by Steam.
- `name`: Trailer/movie title as labeled by Steam.
- `thumbnail_url`: URL to a thumbnail-sized image (reference only, not hosted).
- `webm_url`: URL to the WebM version of the trailer, if available.
- `mp4_url`: URL to the MP4 version of the trailer, if available.

## achievements.csv

**File description:**
Featured achievements per game, as exposed by Steam's public API (partial subset, not exhaustive).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `achievement_name`: Internal name of the achievement.
- `description`: Achievement description text, where available.
- `icon_url`: URL to the achievement's icon image (reference only, not hosted).
- `hidden`: Whether this achievement is a hidden/secret achievement.

## dlc.csv

**File description:**
Base game to downloadable content (DLC) relationships.

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `dlc_steam_appid`: Steam App ID of a piece of downloadable content (DLC) for this base game.

## content_ratings.csv

**File description:**
Regional content rating board classifications per game (e.g. ESRB, PEGI).

**Column descriptions (in order):**

- `game_id`: Internal stable identifier, primary key linking this row to the games table.
- `rating_board`: Regional content rating board (e.g. 'esrb', 'pegi', 'usk').
- `rating_value`: The rating value assigned by this board, if available.
- `descriptors`: Content descriptors associated with this rating (e.g. violence, language).