"""Game data models."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Game:
    """Represents a Steam game with playtime information."""

    appid: int
    name: str
    playtime_forever: int = 0  # in minutes
    playtime_2weeks: int = 0  # in minutes
    img_icon_url: Optional[str] = None
    img_logo_url: Optional[str] = None

    @property
    def playtime_forever_hours(self) -> float:
        """Return playtime in hours."""
        return self.playtime_forever / 60

    @property
    def playtime_2weeks_hours(self) -> float:
        """Return 2-week playtime in hours."""
        return self.playtime_2weeks / 60

    @classmethod
    def from_steam_api(cls, data: dict) -> "Game":
        """Create Game instance from Steam API response data."""
        return cls(
            appid=data["appid"],
            name=data["name"],
            playtime_forever=data.get("playtime_forever", 0),
            playtime_2weeks=data.get("playtime_2weeks", 0),
            img_icon_url=data.get("img_icon_url"),
            img_logo_url=data.get("img_logo_url"),
        )
