# Development Guide

This guide provides information for developers who want to contribute to or modify the Steam Wrapped project.

## 🛠️ Development Setup

### Prerequisites

- **Python 3.13+**: The project uses modern Python features
- **PDM**: Package manager for dependency management
- **Steam Web API Key**: Required for testing API integrations

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd steam-wrapped
   ```

2. **Install PDM** (if not already installed):
   ```bash
   pip install pdm
   ```

3. **Install dependencies**:
   ```bash
   pdm install
   ```

4. **Setup environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your Steam API credentials
   ```

5. **Verify setup**:
   ```bash
   pdm run python main.py
   ```

## 🏗️ Project Structure

```
steam-wrapped/
├── src/                    # Source code
│   ├── services/          # Business logic services
│   ├── models/            # Data models
│   └── ui/                # User interface
├── docs/                  # Documentation
├── fonts/                 # Font assets
├── imgs/                  # Image assets
├── config.py              # Configuration
├── main.py                # Entry point
└── pyproject.toml         # Project configuration
```

## 🔧 Development Workflow

### Code Quality Tools

The project uses several tools to maintain code quality:

```bash
# Format code with Black
pdm run black .

# Lint with Ruff
pdm run ruff check . --fix

# Run all quality checks
pdm run all
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```bash
pdm run pre-commit install
```

### Type Checking

The project uses type annotations throughout. Use mypy for type checking:

```bash
mypy src/ main.py config.py
```

## 🧪 Testing Guidelines

### Unit Testing Structure

Create tests following this structure:
```
tests/
├── test_services/
│   ├── test_steam_api.py
│   └── test_image_service.py
├── test_models/
│   └── test_game.py
└── test_ui/
    └── test_display.py
```

### Testing Best Practices

1. **Mock External Dependencies**: Always mock Steam API calls and file operations
2. **Test Error Conditions**: Ensure proper error handling is tested
3. **Use Factory Functions**: Leverage the factory functions for dependency injection
4. **Test Data Models**: Verify data transformations and validations

### Example Test

```python
import pytest
from unittest.mock import Mock, patch
from src.services.steam_api import SteamAPIService, SteamAPIError

def test_get_owned_games_success():
    # Mock the HTTP client
    mock_client = Mock()
    mock_response = Mock()
    mock_response.json.return_value = {
        "response": {
            "games": [
                {"appid": 123, "name": "Test Game", "playtime_forever": 60}
            ]
        }
    }
    mock_client.get.return_value = mock_response

    # Test the service
    service = SteamAPIService("test_api_key")
    service.client = mock_client

    games = service.get_owned_games("test_user_id")

    assert len(games) == 1
    assert games[0].name == "Test Game"
    assert games[0].playtime_forever == 60
```

## 📝 Adding New Features

### 1. New Service

When adding a new service:

1. Create the service class in `src/services/`
2. Add custom exception if needed
3. Create factory function
4. Add comprehensive type annotations
5. Include proper error handling and logging
6. Write unit tests

### 2. New Model

When adding a new data model:

1. Create dataclass in `src/models/`
2. Add type annotations
3. Include validation if needed
4. Add helper methods/properties
5. Include factory methods for external data
6. Write unit tests

### 3. New UI Component

When adding UI functionality:

1. Add methods to `DisplayService` or create new service
2. Use Rich library for formatting
3. Ensure consistent styling
4. Handle edge cases (empty data, errors)
5. Write unit tests

## 🎨 Code Style Guidelines

### General Principles

1. **Type Annotations**: All functions must have type annotations
2. **Docstrings**: All public methods must have docstrings
3. **Error Handling**: Use custom exceptions with descriptive messages
4. **Logging**: Use structured logging throughout
5. **Constants**: Use class constants instead of magic numbers

### Naming Conventions

- **Classes**: PascalCase (`SteamAPIService`)
- **Functions/Methods**: snake_case (`get_owned_games`)
- **Variables**: snake_case (`recent_games`)
- **Constants**: UPPER_SNAKE_CASE (`STEAM_API_KEY`)
- **Private**: Leading underscore (`_helper_method`)

### Import Organization

```python
# Standard library imports
import logging
from typing import List, Optional

# Third-party imports
import httpx
from PIL import Image

# Local imports
from config import Config
from src.models.game import Game
```

## 🐛 Debugging & Troubleshooting

### Logging

The application uses structured logging. To enable debug logging:

```bash
LOG_LEVEL=DEBUG pdm run python main.py
```

### Common User Issues

**"Missing STEAM_API_KEY or STEAM_USER_ID"**
- Check that your `.env` file exists and contains valid credentials
- Verify your Steam profile is set to public

**"HTTP 403 Forbidden"**
- Your Steam profile game details might be private
- Check your Steam privacy settings

**"No games found"**
- You might not have played any games in the last 2 weeks
- Verify your Steam ID is correct

### Development Issues

1. **Steam API Rate Limiting**: The Steam API has rate limits. Add delays between requests if needed.
2. **Image Download Failures**: Handle cases where game images are not available.
3. **Font Loading**: Ensure font files exist and are accessible.

## 🚀 Deployment Considerations

### Environment Variables

Required environment variables:
- `STEAM_API_KEY`: Your Steam Web API key
- `STEAM_USER_ID`: Target Steam user ID
- `LOG_LEVEL`: Logging level (optional, defaults to INFO)
- `LOCALE`: Date formatting locale (optional, defaults to fr_FR)

### Dependencies

The project uses PDM for dependency management. The `pdm.lock` file ensures reproducible builds.

### Asset Management

Ensure the following assets are available:
- Font files in `fonts/` directory
- Steam icon in `imgs/` directory

## 🤝 Contributing

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the code style guidelines
4. **Add tests** for new functionality
5. **Run quality checks**: `pdm run all`
6. **Update documentation** if needed
7. **Submit pull request** with clear description

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Type annotations are present
- [ ] Error handling is appropriate
- [ ] Logging is included where appropriate

## 📦 Dependencies Overview

### Core Dependencies
- **requests**: HTTP requests for Steam API
- **httpx**: Modern async HTTP client
- **python-dotenv**: Environment variable management
- **Pillow (PIL)**: Image generation and manipulation
- **rich**: Beautiful console output
- **babel**: Internationalization and date formatting

### Development Dependencies
- **black**: Code formatting
- **ruff**: Fast Python linter
- **isort**: Import sorting
- **pre-commit**: Git hooks for code quality

## 🎯 Basic Usage

After setup, generate a Steam Wrapped image:

```bash
# Generate image for the last 2 weeks
pdm run python main.py
```

The application will:
1. Fetch your recent gaming activity from Steam
2. Generate a beautiful summary image
3. Save it as `steam_story.png` in the project directory

## 📚 Additional Resources

- [Steam Web API Documentation](https://developer.valvesoftware.com/wiki/Steam_Web_API)
- [PDM Documentation](https://pdm.fming.dev/)
- [Rich Library Documentation](https://rich.readthedocs.io/)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)