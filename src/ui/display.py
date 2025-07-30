"""Display and user interface logic."""

from typing import List

from rich.console import Console
from rich.table import Table

from src.models.game import Game

console = Console()


class DisplayService:
    """Service for displaying game information to the user."""

    def __init__(self):
        self.console = Console()

    def display_games_table(
        self, title: str, games: List[Game], time_key: str = "playtime_forever"
    ) -> None:
        """Display games in a formatted table."""
        table = Table(title=title)

        table.add_column("Nom", style="cyan", no_wrap=True)
        table.add_column("Temps de jeu", justify="right", style="green")

        for game in games:
            minutes = getattr(game, time_key, 0)
            hours = minutes // 60
            mins = minutes % 60
            table.add_row(game.name, f"{hours} h {mins:02d} min")

        self.console.print(table)

    def display_summary(self, recent_games: List[Game]) -> None:
        """Display a summary of recent gaming activity."""
        if not recent_games:
            self.console.print("❌ Aucun jeu joué dans les 2 dernières semaines.")
            return

        total_time = sum(game.playtime_2weeks for game in recent_games)
        total_hours = total_time // 60
        total_mins = total_time % 60

        self.console.print(
            f"🎮 [bold green]{len(recent_games)} jeux[/bold green] joués dans les 2 dernières semaines"
        )
        self.console.print(
            f"⏰ Temps total: [bold cyan]{total_hours}h {total_mins:02d}min[/bold cyan]"
        )
        self.console.print(
            f"🏆 Jeu le plus joué: [bold yellow]{recent_games[0].name}[/bold yellow]"
        )
        self.console.print()

    def display_error(self, message: str) -> None:
        """Display an error message."""
        self.console.print(f"❌ [bold red]Erreur:[/bold red] {message}")

    def display_success(self, message: str) -> None:
        """Display a success message."""
        self.console.print(f"✅ [bold green]{message}[/bold green]")


def create_display_service() -> DisplayService:
    """Factory function to create display service."""
    return DisplayService()
