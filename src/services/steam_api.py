"""Steam API service for fetching game data."""

import logging
from typing import List

import httpx

from config import Config
from src.models.game import Game

logger = logging.getLogger(__name__)


class SteamAPIError(Exception):
    """Exception raised for Steam API errors."""

    pass


class SteamAPIService:
    """Service for interacting with Steam Web API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.Client(timeout=30.0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def get_player_summaries(self, steamid: str) -> dict:
        """Get player profile information."""
        url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
        params = {"key": self.api_key, "steamids": steamid}

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to get player summaries: {e}")
            raise SteamAPIError(f"Failed to get player summaries: {e}")

    def get_owned_games(
        self, steamid: str, include_free: bool = False, include_appinfo: bool = True
    ) -> List[Game]:
        """Get list of games owned by user."""
        url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
        params = {
            "key": self.api_key,
            "steamid": steamid,
            "include_played_free_games": str(include_free).lower(),
            "include_appinfo": str(include_appinfo).lower(),
        }

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            games_data = response.json()["response"].get("games", [])
            return [Game.from_steam_api(game_data) for game_data in games_data]
        except httpx.HTTPError as e:
            logger.error(f"Failed to get owned games: {e}")
            raise SteamAPIError(f"Failed to get owned games: {e}")
        except KeyError as e:
            logger.error(f"Unexpected API response format: {e}")
            raise SteamAPIError(f"Unexpected API response format: {e}")

    def get_played_games(
        self, steamid: str, include_free: bool = False, include_appinfo: bool = True
    ) -> List[Game]:
        """Get list of played games sorted by total playtime."""
        all_games = self.get_owned_games(steamid, include_free, include_appinfo)
        played_games = [game for game in all_games if game.playtime_forever > 0]
        return sorted(played_games, key=lambda g: g.playtime_forever, reverse=True)

    def get_recently_played_games(
        self, steamid: str, include_free: bool = False, include_appinfo: bool = True
    ) -> List[Game]:
        """Get list of games played in the last 2 weeks."""
        all_games = self.get_owned_games(steamid, include_free, include_appinfo)
        recent_games = [game for game in all_games if game.playtime_2weeks > 0]
        return sorted(recent_games, key=lambda g: g.playtime_2weeks, reverse=True)


def create_steam_service() -> SteamAPIService:
    """Factory function to create Steam API service with config."""
    Config.validate()
    return SteamAPIService(Config.STEAM_API_KEY)
