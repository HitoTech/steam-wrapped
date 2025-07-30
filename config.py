"""Configuration module using environment variables for security."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class Config:
    """Configuration class for Steam Wrapped application."""

    # Steam API settings
    STEAM_API_KEY: str = os.getenv("STEAM_API_KEY", "")
    STEAM_USER_ID: str = os.getenv("STEAM_USER_ID", "")

    # Image generation settings
    IMAGE_WIDTH: int = int(os.getenv("IMAGE_WIDTH", "1080"))
    IMAGE_HEIGHT: int = int(os.getenv("IMAGE_HEIGHT", "1920"))
    LOCALE: str = os.getenv("LOCALE", "fr_FR")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Fonts paths
    FONT_TITLE: str = "fonts/Montserrat-Bold.ttf"
    FONT_GAME: str = "fonts/Montserrat-Regular.ttf"

    @classmethod
    def validate(cls) -> bool:
        """Validate that required environment variables are set."""
        missing_vars = []

        if not cls.STEAM_API_KEY:
            missing_vars.append("STEAM_API_KEY")
        if not cls.STEAM_USER_ID:
            missing_vars.append("STEAM_USER_ID")

        if missing_vars:
            raise ConfigError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please check your .env file or environment variables."
            )

        return True

    @classmethod
    def validate_fonts(cls) -> bool:
        """Validate that font files exist."""
        missing_fonts = []

        if not Path(cls.FONT_TITLE).exists():
            missing_fonts.append(cls.FONT_TITLE)
        if not Path(cls.FONT_GAME).exists():
            missing_fonts.append(cls.FONT_GAME)

        if missing_fonts:
            raise ConfigError(
                f"Missing font files: {', '.join(missing_fonts)}\n"
                f"Please ensure font files are in the fonts/ directory."
            )

        return True

    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
