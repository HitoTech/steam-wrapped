"""Tests for display service."""

from unittest.mock import Mock, patch

from rich.console import Console
from rich.table import Table

from src.models.game import Game
from src.ui.display import DisplayService, create_display_service


class TestDisplayService:
    """Test cases for the DisplayService class."""

    def test_display_service_creation(self):
        """Test that DisplayService can be created."""
        display = DisplayService()

        assert isinstance(display, DisplayService)
        assert isinstance(display.console, Console)

    def test_create_display_service_factory(self):
        """Test the factory function creates a DisplayService."""
        display = create_display_service()

        assert isinstance(display, DisplayService)

    @patch("src.ui.display.Console")
    def test_display_games_table_with_games(self, mock_console_class):
        """Test displaying games table with actual games."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        games = [
            Game(appid=1, name="Game 1", playtime_forever=120),  # 2 hours
            Game(appid=2, name="Game 2", playtime_forever=90),  # 1.5 hours
            Game(appid=3, name="Game 3", playtime_forever=30),  # 30 minutes
        ]

        display.display_games_table("Test Games", games, "playtime_forever")

        # Verify console.print was called
        mock_console.print.assert_called_once()

        # Get the table that was passed to print
        table_arg = mock_console.print.call_args[0][0]
        assert isinstance(table_arg, Table)
        assert table_arg.title == "Test Games"

    @patch("src.ui.display.Console")
    def test_display_games_table_empty_list(self, mock_console_class):
        """Test displaying games table with empty list."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        display.display_games_table("Empty Games", [], "playtime_forever")

        # Verify console.print was called
        mock_console.print.assert_called_once()

        # Get the table that was passed to print
        table_arg = mock_console.print.call_args[0][0]
        assert isinstance(table_arg, Table)
        assert table_arg.title == "Empty Games"

    @patch("src.ui.display.Console")
    def test_display_games_table_with_2weeks_playtime(self, mock_console_class):
        """Test displaying games table with 2-week playtime."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        games = [
            Game(appid=1, name="Recent Game", playtime_2weeks=60),  # 1 hour
        ]

        display.display_games_table("Recent Games", games, "playtime_2weeks")

        # Verify console.print was called
        mock_console.print.assert_called_once()

        # Get the table that was passed to print
        table_arg = mock_console.print.call_args[0][0]
        assert isinstance(table_arg, Table)
        assert table_arg.title == "Recent Games"

    @patch("src.ui.display.Console")
    def test_display_summary_with_games(self, mock_console_class):
        """Test displaying summary with games."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        games = [
            Game(appid=1, name="Top Game", playtime_2weeks=120),  # 2 hours
            Game(appid=2, name="Second Game", playtime_2weeks=60),  # 1 hour
        ]

        display.display_summary(games)

        # Verify console.print was called multiple times
        assert mock_console.print.call_count >= 3  # At least 3 print calls for summary

    @patch("src.ui.display.Console")
    def test_display_summary_empty_list(self, mock_console_class):
        """Test displaying summary with empty games list."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        display.display_summary([])

        # Verify console.print was called once with error message
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "Aucun jeu joué" in call_args

    @patch("src.ui.display.Console")
    def test_display_error(self, mock_console_class):
        """Test displaying error message."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        error_message = "Test error message"
        display.display_error(error_message)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert error_message in call_args
        assert "Erreur" in call_args

    @patch("src.ui.display.Console")
    def test_display_success(self, mock_console_class):
        """Test displaying success message."""
        mock_console = Mock()
        mock_console_class.return_value = mock_console

        display = DisplayService()

        success_message = "Test success message"
        display.display_success(success_message)

        # Verify console.print was called
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert success_message in call_args

    def test_display_games_table_time_formatting(self):
        """Test that time formatting works correctly for different durations."""
        display = DisplayService()

        games = [
            Game(appid=1, name="Short Game", playtime_forever=30),  # 30 minutes
            Game(appid=2, name="Medium Game", playtime_forever=90),  # 1h 30min
            Game(appid=3, name="Long Game", playtime_forever=150),  # 2h 30min
            Game(appid=4, name="Very Long Game", playtime_forever=360),  # 6h 0min
        ]

        # This test verifies the method doesn't raise exceptions
        # The actual formatting is handled by Rich library
        display.display_games_table("Time Test", games, "playtime_forever")

    def test_display_summary_time_calculation(self):
        """Test that summary time calculation works correctly."""
        display = DisplayService()

        games = [
            Game(appid=1, name="Game 1", playtime_2weeks=45),  # 45 minutes
            Game(appid=2, name="Game 2", playtime_2weeks=120),  # 2 hours
            Game(appid=3, name="Game 3", playtime_2weeks=30),  # 30 minutes
        ]

        # Total: 195 minutes = 3h 15min
        # This test verifies the method doesn't raise exceptions
        display.display_summary(games)

    def test_display_service_singleton_behavior(self):
        """Test that each factory call creates a new instance."""
        display1 = create_display_service()
        display2 = create_display_service()

        # Should be different instances
        assert display1 is not display2
        assert isinstance(display1, DisplayService)
        assert isinstance(display2, DisplayService)
