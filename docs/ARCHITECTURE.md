# Steam Wrapped - Architecture Overview

## Project Structure

The project has been restructured to follow clean architecture principles with clear separation of concerns:

```
steam-wrapped/
├── src/                      # Source code organized by layers
│   ├── services/             # Business logic and external services
│   │   ├── steam_api.py     # Steam Web API integration
│   │   └── image_service.py # Image generation service
│   ├── models/              # Data models and domain entities
│   │   └── game.py         # Game data model
│   └── ui/                  # User interface and display logic
│       └── display.py      # Rich console display service
├── config.py               # Configuration management
├── main.py                 # Application entry point (orchestration)
├── fonts/                  # Font assets
├── imgs/                   # Image assets
└── requirements/configs... # Project configuration files
```

## Architecture Layers

### 1. Services Layer (`src/services/`)

**Purpose**: Handle external API calls and business logic

- **`steam_api.py`**: Steam Web API integration
  - `SteamAPIService`: Main service class with context manager support
  - Error handling with custom `SteamAPIError`
  - Methods: `get_owned_games()`, `get_recently_played_games()`, etc.
  - Factory function: `create_steam_service()`

- **`image_service.py`**: Image generation and manipulation
  - `ImageService`: Handles all image generation logic
  - Error handling with custom `ImageGenerationError`
  - Methods: `create_story_image()`, `add_background_image()`, etc.
  - Factory function: `create_image_service()`

### 2. Models Layer (`src/models/`)

**Purpose**: Define data structures and domain entities

- **`game.py`**: Game data model
  - `Game` dataclass with type annotations
  - Properties for time conversion (minutes to hours)
  - Factory method: `from_steam_api()` for API response parsing

### 3. UI Layer (`src/ui/`)

**Purpose**: Handle user interface and display logic

- **`display.py`**: Console output and formatting
  - `DisplayService`: Rich console integration
  - Methods: `display_games_table()`, `display_summary()`, error/success messages
  - Factory function: `create_display_service()`

### 4. Configuration (`config.py`)

**Purpose**: Centralized configuration management

- `Config` class with environment variable loading
- Validation methods (no longer validates on import)
- `ConfigError` custom exception
- Font validation and logging setup

### 5. Main Application (`main.py`)

**Purpose**: Application orchestration and error handling

- Clean entry point with proper error handling
- Service composition and coordination
- Comprehensive exception handling for all service layers

## Key Improvements

### 1. Separation of Concerns
- Each layer has a single responsibility
- No mixing of API calls, UI logic, and image generation
- Clear boundaries between layers

### 2. Error Handling
- Custom exceptions for each service layer
- Proper error propagation and user-friendly messages
- Logging integration throughout the application

### 3. Testability
- Services can be easily mocked and tested independently
- Factory functions for dependency injection
- Clear interfaces between layers

### 4. Type Safety
- Proper type annotations throughout
- Dataclass models with type checking
- Better IDE support and error detection

### 5. Resource Management
- Context manager for HTTP client in Steam API service
- Proper cleanup of resources
- Better memory management

### 6. Configuration Management
- No validation on import (better for testing)
- Separate validation for different concerns (API keys, fonts)
- Better error messages for configuration issues

## Usage Patterns

### Service Creation
```python
# Services are created using factory functions
steam_service = create_steam_service()
image_service = create_image_service()
display_service = create_display_service()
```

### Error Handling
```python
try:
    games = steam_service.get_recently_played_games(user_id)
except SteamAPIError as e:
    display.display_error(f"Steam API error: {e}")
```

### Data Flow
```
main.py → SteamAPIService → Game models → ImageService → Display
```

## Benefits

1. **Maintainability**: Clear structure makes code easier to understand and modify
2. **Testability**: Each component can be tested in isolation
3. **Reusability**: Services can be reused in different contexts
4. **Scalability**: Easy to add new features or modify existing ones
5. **Error Handling**: Comprehensive error handling at each layer
6. **Type Safety**: Better development experience with type checking