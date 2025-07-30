# API Reference

This document provides detailed information about the Steam Wrapped API interfaces, services, and models.

## Services

### Steam API Service (`src.services.steam_api`)

#### `SteamAPIService`

Main service for interacting with Steam Web API.

**Constructor:**
```python
SteamAPIService(api_key: str)
```

**Context Manager Support:**
```python
with create_steam_service() as steam_api:
    # Service automatically manages HTTP client lifecycle
    games = steam_api.get_recently_played_games(user_id)
```

**Methods:**

##### `get_player_summaries(steamid: str) -> dict`
Get player profile information from Steam API.

**Parameters:**
- `steamid`: Steam user ID

**Returns:**
- Dictionary containing player profile data

**Raises:**
- `SteamAPIError`: If API request fails

##### `get_owned_games(steamid: str, include_free: bool = False, include_appinfo: bool = True) -> List[Game]`
Get list of games owned by user.

**Parameters:**
- `steamid`: Steam user ID
- `include_free`: Include free-to-play games
- `include_appinfo`: Include app information (name, icon URLs)

**Returns:**
- List of `Game` objects

**Raises:**
- `SteamAPIError`: If API request fails

##### `get_played_games(steamid: str, include_free: bool = False, include_appinfo: bool = True) -> List[Game]`
Get list of played games sorted by total playtime.

**Parameters:**
- `steamid`: Steam user ID
- `include_free`: Include free-to-play games
- `include_appinfo`: Include app information

**Returns:**
- List of `Game` objects sorted by `playtime_forever` (descending)

**Raises:**
- `SteamAPIError`: If API request fails

##### `get_recently_played_games(steamid: str, include_free: bool = False, include_appinfo: bool = True) -> List[Game]`
Get list of games played in the last 2 weeks.

**Parameters:**
- `steamid`: Steam user ID
- `include_free`: Include free-to-play games
- `include_appinfo`: Include app information

**Returns:**
- List of `Game` objects sorted by `playtime_2weeks` (descending)

**Raises:**
- `SteamAPIError`: If API request fails

#### Factory Function

##### `create_steam_service() -> SteamAPIService`
Create Steam API service instance with configuration validation.

**Returns:**
- Configured `SteamAPIService` instance

**Raises:**
- `ConfigError`: If configuration is invalid

### Image Service (`src.services.image_service`)

#### `ImageService`

Service for generating Steam Wrapped visualization images.

**Constructor:**
```python
ImageService()
```
Automatically loads configuration and fonts.

**Methods:**

##### `create_story_image(games: List[Game], output_path: str = "steam_story.png") -> str`
Create the complete Steam story image.

**Parameters:**
- `games`: List of games to include in visualization
- `output_path`: Path where image should be saved

**Returns:**
- Path to the generated image file

**Raises:**
- `ImageGenerationError`: If image generation fails

##### `download_image(appid: int, format: str) -> Image.Image`
Download game image from Steam CDN.

**Parameters:**
- `appid`: Steam application ID
- `format`: Image format (e.g., "library_600x900.jpg")

**Returns:**
- PIL Image object

**Raises:**
- `ImageGenerationError`: If download fails

#### Factory Function

##### `create_image_service() -> ImageService`
Create image service instance.

**Returns:**
- Configured `ImageService` instance

### Display Service (`src.ui.display`)

#### `DisplayService`

Service for displaying information to the user via Rich console.

**Constructor:**
```python
DisplayService()
```

**Methods:**

##### `display_games_table(title: str, games: List[Game], time_key: str = "playtime_forever") -> None`
Display games in a formatted table.

**Parameters:**
- `title`: Table title
- `games`: List of games to display
- `time_key`: Attribute name for playtime column

##### `display_summary(recent_games: List[Game]) -> None`
Display a summary of recent gaming activity.

**Parameters:**
- `recent_games`: List of recently played games

##### `display_error(message: str) -> None`
Display an error message.

**Parameters:**
- `message`: Error message to display

##### `display_success(message: str) -> None`
Display a success message.

**Parameters:**
- `message`: Success message to display

#### Factory Function

##### `create_display_service() -> DisplayService`
Create display service instance.

**Returns:**
- Configured `DisplayService` instance

## Models

### Game (`src.models.game`)

#### `Game`

Data model representing a Steam game.

**Attributes:**
```python
@dataclass
class Game:
    appid: int                          # Steam application ID
    name: str                           # Game name
    playtime_forever: int = 0           # Total playtime in minutes
    playtime_2weeks: int = 0            # Recent playtime in minutes
    img_icon_url: Optional[str] = None  # Icon URL
    img_logo_url: Optional[str] = None  # Logo URL
```

**Properties:**

##### `playtime_forever_hours -> float`
Return total playtime in hours.

##### `playtime_2weeks_hours -> float`
Return 2-week playtime in hours.

**Class Methods:**

##### `from_steam_api(data: dict) -> Game`
Create Game instance from Steam API response data.

**Parameters:**
- `data`: Dictionary from Steam API response

**Returns:**
- `Game` instance

## Exceptions

### `SteamAPIError`
Raised when Steam API operations fail.

### `ImageGenerationError`
Raised when image generation operations fail.

### `ConfigError`
Raised when configuration validation fails.

## Configuration

### `Config` (`config`)

Configuration management class.

**Class Methods:**

##### `validate() -> bool`
Validate that required environment variables are set.

**Raises:**
- `ConfigError`: If required variables are missing

##### `validate_fonts() -> bool`
Validate that font files exist.

**Raises:**
- `ConfigError`: If font files are missing

##### `setup_logging() -> None`
Setup logging configuration based on LOG_LEVEL.