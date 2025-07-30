"""Configuration module using environment variables for security."""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                f"Please check your .env file or environment variables."
            )

        return True


# Validate configuration on import
Config.validate()
