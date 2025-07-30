"""Steam Wrapped - Main application entry point."""

import logging
import sys

from config import Config, ConfigError
from src.services.image_service import ImageGenerationError, create_image_service
from src.services.steam_api import SteamAPIError, create_steam_service
from src.ui.display import create_display_service


def main() -> None:
    """Main application entry point."""
    # Setup logging
    Config.setup_logging()
    logger = logging.getLogger(__name__)

    # Create services
    display = create_display_service()

    try:
        # Validate configuration
        Config.validate()
        Config.validate_fonts()

        logger.info("Starting Steam Wrapped application")

        # Create Steam API service
        with create_steam_service() as steam_api:
            # Fetch recent games
            logger.info(f"Fetching recent games for user {Config.STEAM_USER_ID}")
            recent_games = steam_api.get_recently_played_games(Config.STEAM_USER_ID)

            if not recent_games:
                display.display_error("Aucun jeu joué dans les 2 dernières semaines.")
                return

            # Display summary
            display.display_summary(recent_games)

            # Display games table (optional)
            display.display_games_table(
                "Jeux récents (2 dernières semaines)",
                recent_games[:10],
                "playtime_2weeks",
            )

            # Generate image
            logger.info("Generating Steam story image")
            image_service = create_image_service()
            output_path = image_service.create_story_image(recent_games)

            display.display_success(f"Image générée avec succès: {output_path}")

    except ConfigError as e:
        display.display_error(f"Configuration invalide: {e}")
        sys.exit(1)
    except SteamAPIError as e:
        display.display_error(f"Erreur API Steam: {e}")
        sys.exit(1)
    except ImageGenerationError as e:
        display.display_error(f"Erreur génération d'image: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        display.display_error(f"Erreur inattendue: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
