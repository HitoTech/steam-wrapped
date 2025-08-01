"""Tests for Steam API service."""

from unittest.mock import Mock, patch

import httpx
import pytest

from config import Config
from src.models.game import Game
from src.services.steam_api import SteamAPIError, SteamAPIService, create_steam_service


class TestSteamAPIService:
    """Test cases for the SteamAPIService class."""

    def test_steam_api_service_creation(self):
        """Test that SteamAPIService can be created."""
        service = SteamAPIService("test_api_key")

        assert service.api_key == "test_api_key"
        assert isinstance(service.client, httpx.Client)

    def test_steam_api_service_context_manager(self):
        """Test that SteamAPIService works as a context manager."""
        service = SteamAPIService("test_api_key")

        with service as ctx_service:
            assert ctx_service is service

        # Client should be closed after context exit
        assert service.client.is_closed

    @patch("httpx.Client.get")
    def test_get_player_summaries_success(self, mock_get):
        """Test successful player summaries retrieval."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "players": [
                    {
                        "steamid": "123456789",
                        "personaname": "TestPlayer",
                        "profileurl": "http://steamcommunity.com/id/testplayer",
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = SteamAPIService("test_api_key")

        result = service.get_player_summaries("123456789")

        # Verify the result
        assert result["response"]["players"][0]["personaname"] == "TestPlayer"

        # Verify the request was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "api.steampowered.com" in call_args[0][0]
        assert call_args[1]["params"]["key"] == "test_api_key"
        assert call_args[1]["params"]["steamids"] == "123456789"

    @patch("httpx.Client.get")
    def test_get_player_summaries_http_error(self, mock_get):
        """Test player summaries retrieval with HTTP error."""
        # Mock HTTP error
        mock_get.side_effect = httpx.HTTPError("Connection failed")

        service = SteamAPIService("test_api_key")

        with pytest.raises(SteamAPIError) as exc_info:
            service.get_player_summaries("123456789")

        assert "Failed to get player summaries" in str(exc_info.value)

    @patch("httpx.Client.get")
    def test_get_owned_games_success(self, mock_get):
        """Test successful owned games retrieval."""
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "game_count": 2,
                "games": [
                    {
                        "appid": 123,
                        "name": "Test Game 1",
                        "playtime_forever": 120,
                        "playtime_2weeks": 30,
                        "img_icon_url": "icon1.jpg",
                        "img_logo_url": "logo1.jpg",
                    },
                    {
                        "appid": 456,
                        "name": "Test Game 2",
                        "playtime_forever": 90,
                        "playtime_2weeks": 0,
                        "img_icon_url": "icon2.jpg",
                        "img_logo_url": "logo2.jpg",
                    },
                ],
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = SteamAPIService("test_api_key")

        result = service.get_owned_games("123456789")

        # Verify the result contains Game objects
        assert len(result) == 2
        assert isinstance(result[0], Game)
        assert result[0].appid == 123
        assert result[0].name == "Test Game 1"
        assert result[0].playtime_forever == 120
        assert result[0].playtime_2weeks == 30

        assert isinstance(result[1], Game)
        assert result[1].appid == 456
        assert result[1].name == "Test Game 2"
        assert result[1].playtime_forever == 90
        assert result[1].playtime_2weeks == 0

    @patch("httpx.Client.get")
    def test_get_owned_games_empty_response(self, mock_get):
        """Test owned games retrieval with empty response."""
        # Mock response with no games
        mock_response = Mock()
        mock_response.json.return_value = {"response": {"game_count": 0, "games": []}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = SteamAPIService("test_api_key")

        result = service.get_owned_games("123456789")

        # Verify empty list is returned
        assert result == []

    @patch("httpx.Client.get")
    def test_get_owned_games_http_error(self, mock_get):
        """Test owned games retrieval with HTTP error."""
        # Mock HTTP error
        mock_get.side_effect = httpx.HTTPError("Connection failed")

        service = SteamAPIService("test_api_key")

        with pytest.raises(SteamAPIError) as exc_info:
            service.get_owned_games("123456789")

        assert "Failed to get owned games" in str(exc_info.value)

    @patch("httpx.Client.get")
    def test_get_owned_games_missing_response_key(self, mock_get):
        """Test owned games retrieval with missing response key."""
        # Mock response with missing 'response' key
        mock_response = Mock()
        mock_response.json.return_value = {
            # Missing 'response' key
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = SteamAPIService("test_api_key")

        with pytest.raises(SteamAPIError) as exc_info:
            service.get_owned_games("123456789")

        assert "Unexpected API response format" in str(exc_info.value)

    @patch("httpx.Client.get")
    def test_get_played_games(self, mock_get):
        """Test get_played_games filters and sorts correctly."""
        # Mock response with mixed played/unplayed games
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "games": [
                    {
                        "appid": 1,
                        "name": "Unplayed Game",
                        "playtime_forever": 0,
                        "playtime_2weeks": 0,
                    },
                    {
                        "appid": 2,
                        "name": "Most Played",
                        "playtime_forever": 300,
                        "playtime_2weeks": 60,
                    },
                    {
                        "appid": 3,
                        "name": "Less Played",
                        "playtime_forever": 120,
                        "playtime_2weeks": 30,
                    },
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = SteamAPIService("test_api_key")

        result = service.get_played_games("123456789")

        # Should only return games with playtime > 0, sorted by playtime
        assert len(result) == 2
        assert result[0].name == "Most Played"  # 300 minutes
        assert result[1].name == "Less Played"  # 120 minutes

    @patch("httpx.Client.get")
    def test_get_recently_played_games(self, mock_get):
        """Test get_recently_played_games filters and sorts correctly."""
        # Mock response with mixed recent/not recent games
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {
                "games": [
                    {
                        "appid": 1,
                        "name": "Old Game",
                        "playtime_forever": 100,
                        "playtime_2weeks": 0,
                    },
                    {
                        "appid": 2,
                        "name": "Most Recent",
                        "playtime_forever": 200,
                        "playtime_2weeks": 90,
                    },
                    {
                        "appid": 3,
                        "name": "Less Recent",
                        "playtime_forever": 150,
                        "playtime_2weeks": 30,
                    },
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        service = SteamAPIService("test_api_key")

        result = service.get_recently_played_games("123456789")

        # Should only return games with 2-week playtime > 0, sorted by 2-week playtime
        assert len(result) == 2
        assert result[0].name == "Most Recent"  # 90 minutes
        assert result[1].name == "Less Recent"  # 30 minutes

    def test_steam_api_error_inheritance(self):
        """Test that SteamAPIError properly inherits from Exception."""
        error = SteamAPIError("Test error message")

        assert isinstance(error, Exception)
        assert str(error) == "Test error message"


class TestCreateSteamService:
    """Test cases for the create_steam_service factory function."""

    @patch("src.services.steam_api.Config.validate")
    def test_create_steam_service_success(self, mock_validate):
        """Test successful service creation."""
        mock_validate.return_value = True

        with patch.object(Config, "STEAM_API_KEY", "test_api_key"):
            service = create_steam_service()

            assert isinstance(service, SteamAPIService)
            assert service.api_key == "test_api_key"
            mock_validate.assert_called_once()

    @patch("src.services.steam_api.Config.validate")
    def test_create_steam_service_validation_failure(self, mock_validate):
        """Test service creation with validation failure."""
        from config import ConfigError

        mock_validate.side_effect = ConfigError("Validation failed")

        with pytest.raises(ConfigError):
            create_steam_service()
