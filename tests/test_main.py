"""Integration tests for main application."""

import sys
from unittest.mock import Mock, patch

from src.models.game import Game


class TestMainApplication:
    """Integration tests for the main application."""

    @patch("main.Config.setup_logging")
    @patch("main.Config.validate")
    @patch("main.Config.validate_fonts")
    @patch("main.create_steam_service")
    @patch("main.create_display_service")
    @patch("main.create_image_service")
    def test_main_successful_execution(
        self,
        mock_create_image_service,
        mock_create_display_service,
        mock_create_steam_service,
        mock_validate_fonts,
        mock_validate,
        mock_setup_logging,
    ):
        """Test successful main application execution."""
        # Mock services
        mock_display = Mock()
        mock_create_display_service.return_value = mock_display

        mock_steam_api = Mock()
        mock_steam_api.__enter__ = Mock(return_value=mock_steam_api)
        mock_steam_api.__exit__ = Mock(return_value=None)
        mock_create_steam_service.return_value = mock_steam_api

        mock_image_service = Mock()
        mock_create_image_service.return_value = mock_image_service

        # Mock games data
        test_games = [
            Game(appid=1, name="Test Game 1", playtime_2weeks=120),
            Game(appid=2, name="Test Game 2", playtime_2weeks=60),
        ]
        mock_steam_api.get_recently_played_games.return_value = test_games

        mock_image_service.create_story_image.return_value = "test_output.png"

        # Import and run main
        with patch.object(sys, "exit") as mock_exit:
            import main

            main.main()

            # Verify setup was called
            mock_setup_logging.assert_called_once()
            mock_validate.assert_called_once()
            mock_validate_fonts.assert_called_once()

            # Verify services were created
            mock_create_display_service.assert_called_once()
            mock_create_steam_service.assert_called_once()
            mock_create_image_service.assert_called_once()

            # Verify Steam API was called
            mock_steam_api.get_recently_played_games.assert_called_once()

            # Verify display methods were called
            mock_display.display_summary.assert_called_once_with(test_games)
            mock_display.display_games_table.assert_called_once()
            mock_display.display_success.assert_called_once()

            # Verify image generation was called
            mock_image_service.create_story_image.assert_called_once_with(test_games)

            # Verify no exit was called (successful execution)
            mock_exit.assert_not_called()

    @patch("main.Config.setup_logging")
    @patch("main.Config.validate")
    @patch("main.create_display_service")
    def test_main_no_recent_games(
        self, mock_create_display_service, mock_validate, mock_setup_logging
    ):
        """Test main application when no recent games are found."""
        # Mock display service
        mock_display = Mock()
        mock_create_display_service.return_value = mock_display

        # Mock Steam API with no games
        mock_steam_api = Mock()
        mock_steam_api.__enter__ = Mock(return_value=mock_steam_api)
        mock_steam_api.__exit__ = Mock(return_value=None)

        with patch("main.create_steam_service", return_value=mock_steam_api):
            mock_steam_api.get_recently_played_games.return_value = []

            # Import and run main
            import main

            main.main()

            # Verify error was displayed
            mock_display.display_error.assert_called_once_with(
                "Aucun jeu joué dans les 2 dernières semaines."
            )

            # Verify no exit was called (main just returns)
            # The main function doesn't call sys.exit(0) when no games found

    @patch("main.Config.setup_logging")
    @patch("main.Config.validate")
    @patch("main.create_display_service")
    def test_main_config_error(
        self, mock_create_display_service, mock_validate, mock_setup_logging
    ):
        """Test main application with configuration error."""
        from config import ConfigError

        # Mock display service
        mock_display = Mock()
        mock_create_display_service.return_value = mock_display

        # Mock validation to raise ConfigError
        with patch("main.Config.validate", side_effect=ConfigError("Config error")):
            # Import and run main
            with patch.object(sys, "exit") as mock_exit:
                import main

                main.main()

                # Verify error was displayed
                mock_display.display_error.assert_called_once_with(
                    "Configuration invalide: Config error"
                )

                # Verify exit was called with error code
                mock_exit.assert_called_once_with(1)

    @patch("main.Config.setup_logging")
    @patch("main.Config.validate")
    @patch("main.create_display_service")
    def test_main_steam_api_error(
        self, mock_create_display_service, mock_validate, mock_setup_logging
    ):
        """Test main application with Steam API error."""
        from src.services.steam_api import SteamAPIError

        # Mock display service
        mock_display = Mock()
        mock_create_display_service.return_value = mock_display

        # Mock Steam API to raise error during context manager entry
        mock_steam_api = Mock()
        mock_steam_api.__enter__ = Mock(side_effect=SteamAPIError("API error"))
        mock_steam_api.__exit__ = Mock(return_value=None)

        with patch("main.create_steam_service", return_value=mock_steam_api):
            # Import and run main
            with patch.object(sys, "exit") as mock_exit:
                import main

                main.main()

                # Verify error was displayed
                mock_display.display_error.assert_called_once_with(
                    "Erreur API Steam: API error"
                )

                # Verify exit was called with error code
                mock_exit.assert_called_once_with(1)

    @patch("main.Config.setup_logging")
    @patch("main.Config.validate")
    @patch("main.create_display_service")
    def test_main_image_generation_error(
        self, mock_create_display_service, mock_validate, mock_setup_logging
    ):
        """Test main application with image generation error."""
        from src.services.image_service import ImageGenerationError

        # Mock display service
        mock_display = Mock()
        mock_create_display_service.return_value = mock_display

        # Mock Steam API
        mock_steam_api = Mock()
        mock_steam_api.__enter__ = Mock(return_value=mock_steam_api)
        mock_steam_api.__exit__ = Mock(return_value=None)

        test_games = [Game(appid=1, name="Test Game", playtime_2weeks=60)]
        mock_steam_api.get_recently_played_games.return_value = test_games

        # Mock image service to raise error
        mock_image_service = Mock()
        mock_image_service.create_story_image.side_effect = ImageGenerationError(
            "Image error"
        )

        with patch("main.create_steam_service", return_value=mock_steam_api):
            with patch("main.create_image_service", return_value=mock_image_service):
                # Import and run main
                with patch.object(sys, "exit") as mock_exit:
                    import main

                    main.main()

                    # Verify error was displayed
                    mock_display.display_error.assert_called_once_with(
                        "Erreur génération d'image: Image error"
                    )

                    # Verify exit was called with error code
                    mock_exit.assert_called_once_with(1)

    @patch("main.Config.setup_logging")
    @patch("main.Config.validate")
    @patch("main.create_display_service")
    def test_main_unexpected_error(
        self, mock_create_display_service, mock_validate, mock_setup_logging
    ):
        """Test main application with unexpected error."""
        # Mock display service
        mock_display = Mock()
        mock_create_display_service.return_value = mock_display

        # Mock validation to raise unexpected error
        with patch("main.Config.validate", side_effect=Exception("Unexpected error")):
            # Import and run main
            with patch.object(sys, "exit") as mock_exit:
                import main

                main.main()

                # Verify error was displayed
                mock_display.display_error.assert_called_once_with(
                    "Erreur inattendue: Unexpected error"
                )

                # Verify exit was called with error code
                mock_exit.assert_called_once_with(1)
