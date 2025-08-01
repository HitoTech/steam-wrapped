"""Tests for data models."""

from src.models.game import Game


class TestGame:
    """Test cases for the Game model."""

    def test_game_creation_with_minimal_data(self):
        """Test creating a Game with minimal required data."""
        game = Game(appid=123, name="Test Game")

        assert game.appid == 123
        assert game.name == "Test Game"
        assert game.playtime_forever == 0
        assert game.playtime_2weeks == 0
        assert game.img_icon_url is None
        assert game.img_logo_url is None

    def test_game_creation_with_all_data(self):
        """Test creating a Game with all optional data."""
        game = Game(
            appid=456,
            name="Full Test Game",
            playtime_forever=120,  # 2 hours
            playtime_2weeks=30,  # 30 minutes
            img_icon_url="http://example.com/icon.jpg",
            img_logo_url="http://example.com/logo.jpg",
        )

        assert game.appid == 456
        assert game.name == "Full Test Game"
        assert game.playtime_forever == 120
        assert game.playtime_2weeks == 30
        assert game.img_icon_url == "http://example.com/icon.jpg"
        assert game.img_logo_url == "http://example.com/logo.jpg"

    def test_playtime_forever_hours_property(self):
        """Test the playtime_forever_hours property calculation."""
        game = Game(appid=123, name="Test Game", playtime_forever=90)  # 90 minutes

        assert game.playtime_forever_hours == 1.5

    def test_playtime_2weeks_hours_property(self):
        """Test the playtime_2weeks_hours property calculation."""
        game = Game(appid=123, name="Test Game", playtime_2weeks=45)  # 45 minutes

        assert game.playtime_2weeks_hours == 0.75

    def test_playtime_hours_with_zero_minutes(self):
        """Test hour properties with zero playtime."""
        game = Game(appid=123, name="Test Game")

        assert game.playtime_forever_hours == 0.0
        assert game.playtime_2weeks_hours == 0.0

    def test_from_steam_api_with_complete_data(self):
        """Test creating Game from Steam API response with complete data."""
        steam_data = {
            "appid": 789,
            "name": "Steam API Game",
            "playtime_forever": 180,
            "playtime_2weeks": 60,
            "img_icon_url": "http://steam.com/icon.jpg",
            "img_logo_url": "http://steam.com/logo.jpg",
        }

        game = Game.from_steam_api(steam_data)

        assert game.appid == 789
        assert game.name == "Steam API Game"
        assert game.playtime_forever == 180
        assert game.playtime_2weeks == 60
        assert game.img_icon_url == "http://steam.com/icon.jpg"
        assert game.img_logo_url == "http://steam.com/logo.jpg"

    def test_from_steam_api_with_missing_optional_fields(self):
        """Test creating Game from Steam API response with missing optional fields."""
        steam_data = {"appid": 999, "name": "Minimal Steam Game"}

        game = Game.from_steam_api(steam_data)

        assert game.appid == 999
        assert game.name == "Minimal Steam Game"
        assert game.playtime_forever == 0
        assert game.playtime_2weeks == 0
        assert game.img_icon_url is None
        assert game.img_logo_url is None

    def test_from_steam_api_with_partial_optional_fields(self):
        """Test creating Game from Steam API response with some optional fields."""
        steam_data = {
            "appid": 555,
            "name": "Partial Steam Game",
            "playtime_forever": 240,
            "img_icon_url": "http://steam.com/partial_icon.jpg",
        }

        game = Game.from_steam_api(steam_data)

        assert game.appid == 555
        assert game.name == "Partial Steam Game"
        assert game.playtime_forever == 240
        assert game.playtime_2weeks == 0
        assert game.img_icon_url == "http://steam.com/partial_icon.jpg"
        assert game.img_logo_url is None

    def test_game_equality(self):
        """Test that Game instances with same data are equal."""
        game1 = Game(appid=123, name="Test Game", playtime_forever=100)
        game2 = Game(appid=123, name="Test Game", playtime_forever=100)

        assert game1 == game2

    def test_game_inequality(self):
        """Test that Game instances with different data are not equal."""
        game1 = Game(appid=123, name="Test Game", playtime_forever=100)
        game2 = Game(appid=123, name="Different Game", playtime_forever=100)
        game3 = Game(appid=456, name="Test Game", playtime_forever=100)

        assert game1 != game2
        assert game1 != game3
