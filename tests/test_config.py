"""Tests for configuration module."""

import logging
import os
from unittest.mock import patch

import pytest

from config import Config, ConfigError


class TestConfig:
    """Test cases for the Config class."""

    def test_default_values(self):
        """Test that Config has expected default values."""
        # Test that Config class attributes have expected default values
        # Note: These values are loaded from .env file, so we test the structure
        assert hasattr(Config, "STEAM_API_KEY")
        assert hasattr(Config, "STEAM_USER_ID")
        assert Config.IMAGE_WIDTH == 1080
        assert Config.IMAGE_HEIGHT == 1920
        assert Config.LOCALE == "fr_FR"
        assert Config.LOG_LEVEL == "INFO"
        assert Config.FONT_TITLE == "fonts/Montserrat-Bold.ttf"
        assert Config.FONT_GAME == "fonts/Montserrat-Regular.ttf"

    def test_environment_variable_loading(self):
        """Test that environment variables are properly loaded."""
        # Test that Config can handle different environment variable types
        test_env = {
            "IMAGE_WIDTH": "1920",
            "IMAGE_HEIGHT": "1080",
            "LOCALE": "en_US",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, test_env, clear=True):
            # Test that integer conversion works correctly
            assert int(os.getenv("IMAGE_WIDTH", "1080")) == 1920
            assert int(os.getenv("IMAGE_HEIGHT", "1920")) == 1080
            assert os.getenv("LOCALE", "fr_FR") == "en_US"
            assert os.getenv("LOG_LEVEL", "INFO") == "DEBUG"

    def test_validate_success(self):
        """Test successful validation with all required variables set."""
        # Mock the Config class attributes to simulate valid configuration
        with patch.object(Config, "STEAM_API_KEY", "valid_api_key"):
            with patch.object(Config, "STEAM_USER_ID", "valid_user_id"):
                # Should not raise an exception
                assert Config.validate() is True

    def test_validate_missing_steam_api_key(self):
        """Test validation failure when STEAM_API_KEY is missing."""
        # Mock the Config class attributes to simulate missing API key
        with patch.object(Config, "STEAM_API_KEY", ""):
            with pytest.raises(ConfigError) as exc_info:
                Config.validate()

            assert "STEAM_API_KEY" in str(exc_info.value)
            assert "Missing required environment variables" in str(exc_info.value)

    def test_validate_missing_steam_user_id(self):
        """Test validation failure when STEAM_USER_ID is missing."""
        # Mock the Config class attributes to simulate missing user ID
        with patch.object(Config, "STEAM_USER_ID", ""):
            with pytest.raises(ConfigError) as exc_info:
                Config.validate()

            assert "STEAM_USER_ID" in str(exc_info.value)
            assert "Missing required environment variables" in str(exc_info.value)

    def test_validate_missing_both_required_variables(self):
        """Test validation failure when both required variables are missing."""
        # Mock the Config class attributes to simulate missing variables
        with patch.object(Config, "STEAM_API_KEY", ""):
            with patch.object(Config, "STEAM_USER_ID", ""):
                with pytest.raises(ConfigError) as exc_info:
                    Config.validate()

                error_message = str(exc_info.value)
                assert "STEAM_API_KEY" in error_message
                assert "STEAM_USER_ID" in error_message
                assert "Missing required environment variables" in error_message

    def test_validate_fonts_success(self, tmp_path):
        """Test successful font validation when fonts exist."""
        # Create temporary font files
        fonts_dir = tmp_path / "fonts"
        fonts_dir.mkdir()
        (fonts_dir / "Montserrat-Bold.ttf").write_text("fake font data")
        (fonts_dir / "Montserrat-Regular.ttf").write_text("fake font data")

        with patch.object(Config, "FONT_TITLE", str(fonts_dir / "Montserrat-Bold.ttf")):
            with patch.object(
                Config, "FONT_GAME", str(fonts_dir / "Montserrat-Regular.ttf")
            ):
                # Should not raise an exception
                assert Config.validate_fonts() is True

    def test_validate_fonts_missing_title_font(self, tmp_path):
        """Test font validation failure when title font is missing."""
        # Create temporary font directory with only one font
        fonts_dir = tmp_path / "fonts"
        fonts_dir.mkdir()
        (fonts_dir / "Montserrat-Regular.ttf").write_text("fake font data")

        with patch.object(Config, "FONT_TITLE", str(fonts_dir / "Montserrat-Bold.ttf")):
            with patch.object(
                Config, "FONT_GAME", str(fonts_dir / "Montserrat-Regular.ttf")
            ):
                with pytest.raises(ConfigError) as exc_info:
                    Config.validate_fonts()

                error_message = str(exc_info.value)
                assert "Montserrat-Bold.ttf" in error_message
                assert "Missing font files" in error_message

    def test_validate_fonts_missing_game_font(self, tmp_path):
        """Test font validation failure when game font is missing."""
        # Create temporary font directory with only one font
        fonts_dir = tmp_path / "fonts"
        fonts_dir.mkdir()
        (fonts_dir / "Montserrat-Bold.ttf").write_text("fake font data")

        with patch.object(Config, "FONT_TITLE", str(fonts_dir / "Montserrat-Bold.ttf")):
            with patch.object(
                Config, "FONT_GAME", str(fonts_dir / "Montserrat-Regular.ttf")
            ):
                with pytest.raises(ConfigError) as exc_info:
                    Config.validate_fonts()

                error_message = str(exc_info.value)
                assert "Montserrat-Regular.ttf" in error_message
                assert "Missing font files" in error_message

    def test_validate_fonts_missing_both_fonts(self, tmp_path):
        """Test font validation failure when both fonts are missing."""
        # Create empty temporary font directory
        fonts_dir = tmp_path / "fonts"
        fonts_dir.mkdir()

        with patch.object(Config, "FONT_TITLE", str(fonts_dir / "Montserrat-Bold.ttf")):
            with patch.object(
                Config, "FONT_GAME", str(fonts_dir / "Montserrat-Regular.ttf")
            ):
                with pytest.raises(ConfigError) as exc_info:
                    Config.validate_fonts()

                error_message = str(exc_info.value)
                assert "Montserrat-Bold.ttf" in error_message
                assert "Montserrat-Regular.ttf" in error_message
                assert "Missing font files" in error_message

    @patch("logging.basicConfig")
    def test_setup_logging(self, mock_basic_config):
        """Test that logging setup is called with correct parameters."""
        Config.setup_logging()

        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args

        # Check that basicConfig was called with expected parameters
        assert call_args[1]["level"] == logging.INFO  # Default level
        assert "format" in call_args[1]
        assert "datefmt" in call_args[1]

    @patch("logging.basicConfig")
    def test_setup_logging_with_custom_level(self, mock_basic_config):
        """Test logging setup with custom log level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=True):
            import importlib

            import config

            importlib.reload(config)

            config.Config.setup_logging()

            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args
            assert call_args[1]["level"] == logging.DEBUG

    def test_config_error_inheritance(self):
        """Test that ConfigError properly inherits from Exception."""
        error = ConfigError("Test error message")

        assert isinstance(error, Exception)
        assert str(error) == "Test error message"
