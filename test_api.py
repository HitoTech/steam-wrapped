import os

import httpx
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_USER_ID = os.getenv("STEAM_USER_ID")

console = Console()


def display_games_table(title: str, games: list, time_key: str = "playtime_forever"):
    table = Table(title=title)

    table.add_column("Nom", style="cyan", no_wrap=True)
    table.add_column("Temps de jeu", justify="right", style="green")

    for game in games:
        minutes = game.get(time_key, 0)
        hours = minutes // 60
        mins = minutes % 60
        table.add_row(game["name"], f"{hours} h {mins:02d} min")

    console.print(table)


def get_player_summaries(steamid: str):
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": STEAM_API_KEY, "steamids": steamid}
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()


def get_owned_games(
    steamid: str, include_free: bool = False, include_appinfo: bool = True
):
    url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steamid,
        "include_played_free_games": str(include_free).lower(),
        "include_appinfo": str(include_appinfo).lower(),
    }
    response = httpx.get(url, params=params)
    response.raise_for_status()
    return response.json()["response"].get("games", [])


def get_played_games(
    steamid: str, include_free: bool = False, include_appinfo: bool = True
):
    all_games = get_owned_games(steamid, include_free, include_appinfo)

    played_games = [game for game in all_games if game.get("playtime_forever", 0) > 0]
    played_games.sort(key=lambda g: g["playtime_forever"], reverse=True)

    return played_games


def get_played_games_on_last_2_weeks(
    steamid: str, include_free: bool = False, include_appinfo: bool = True
):
    all_games = get_owned_games(steamid, include_free, include_appinfo)

    played_games = [game for game in all_games if game.get("playtime_2weeks", 0) > 0]
    played_games.sort(key=lambda g: g["playtime_2weeks"], reverse=True)

    return played_games


if __name__ == "__main__":
    if not STEAM_API_KEY or not STEAM_USER_ID:
        print("⚠️ STEAM_API_KEY ou STEAM_USER_ID manquant dans .env")
    else:
        played_games = get_played_games(STEAM_USER_ID)
        played_games_last_2_weeks = get_played_games_on_last_2_weeks(STEAM_USER_ID)

        display_games_table("🎮 Tous les jeux joués", played_games)
        display_games_table(
            "🕒 Jeux joués les 2 dernières semaines",
            played_games_last_2_weeks,
            "playtime_2weeks",
        )
