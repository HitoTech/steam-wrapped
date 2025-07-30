"""Image generation service for creating Steam Wrapped visualizations."""

import logging
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import List

import requests
from babel.dates import format_date
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import Config
from src.models.game import Game

logger = logging.getLogger(__name__)


class ImageGenerationError(Exception):
    """Exception raised for image generation errors."""

    pass


class ImageService:
    """Service for generating Steam Wrapped images."""

    def __init__(self):
        self.width = Config.IMAGE_WIDTH
        self.height = Config.IMAGE_HEIGHT
        self.margin = 60

        # Load fonts
        try:
            self.font_title = ImageFont.truetype(Config.FONT_TITLE, 80)
            self.font_game = ImageFont.truetype(Config.FONT_GAME, 60)
            self.font_time = ImageFont.truetype(Config.FONT_GAME, 40)
        except OSError as e:
            logger.error(f"Failed to load fonts: {e}")
            raise ImageGenerationError(f"Failed to load fonts: {e}")

    def download_image(self, appid: int, format: str) -> Image.Image:
        """Download game image from Steam CDN."""
        url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/{format}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except (requests.RequestException, OSError) as e:
            logger.error(f"Failed to download image for app {appid}: {e}")
            # Return a placeholder image or raise exception
            raise ImageGenerationError(f"Failed to download image for app {appid}: {e}")

    def add_background_image(
        self, games: List[Game]
    ) -> tuple[Image.Image, ImageDraw.Draw]:
        """Add blurred background image of most played game."""
        if not games:
            raise ImageGenerationError("No games provided for background")

        most_played = max(games, key=lambda g: g.playtime_forever)
        bg_image = (
            self.download_image(most_played.appid, "library_600x900.jpg")
            .resize((self.width, self.height))
            .filter(ImageFilter.GaussianBlur(40))
        )
        canvas = Image.new("RGBA", (self.width, self.height))
        canvas.paste(bg_image, (0, 0))
        draw = ImageDraw.Draw(canvas)
        return canvas, draw

    def add_header(self, canvas: Image.Image) -> None:
        """Add header with title and date range."""
        today = datetime.today()
        start = today - timedelta(days=14)
        date_text = f"{format_date(start, format='dd MMMM', locale=Config.LOCALE)} - {format_date(today, format='dd MMMM yyyy', locale=Config.LOCALE)}"

        banner_height = 220
        banner_rect = [(0, 0), (self.width, self.margin + banner_height)]

        # Create a semi-transparent black rectangle
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        overlay_draw.rectangle(banner_rect, fill=(0, 0, 0, 120))
        canvas.alpha_composite(overlay)

        self.draw_text_with_blur_shadow(
            canvas, (self.margin + 100, self.margin), "Steam Wrapped", self.font_title
        )
        self.draw_text_with_blur_shadow(
            canvas, (self.margin, self.margin + 100), date_text, self.font_game
        )

    def add_steam_logo(self, canvas: Image.Image) -> Image.Image:
        """Add Steam logo to the canvas."""
        logo_path = Path("imgs/steam_icon.png")
        if not logo_path.exists():
            logger.warning("Steam logo not found, skipping")
            return canvas

        steam_logo = Image.open(logo_path).convert("RGBA")
        steam_logo = steam_logo.resize((80, 80))
        canvas.paste(steam_logo, (self.margin, self.margin), steam_logo)
        return canvas

    def add_background_gradient(self, canvas: Image.Image) -> Image.Image:
        """Add gradient overlay to improve text readability."""
        gradient = Image.new("L", (1, self.height), color=0xFF)
        for y in range(self.height):
            gradient.putpixel(
                (0, y),
                max(
                    0,
                    min(255, int((y - self.height * 0.4) / (self.height * 0.7) * 255)),
                ),
            )

        alpha_gradient = gradient.resize((self.width, self.height))
        black_img = Image.new("RGBA", (self.width, self.height), color=(0, 0, 0, 255))
        black_img.putalpha(alpha_gradient)
        canvas = Image.alpha_composite(canvas, black_img)
        return canvas

    def draw_text_with_blur_shadow(
        self,
        base_img: Image.Image,
        position: tuple[int, int],
        text: str,
        font: ImageFont.FreeTypeFont,
        text_color: str = "white",
        shadow_color: str = "black",
        offset: tuple[int, int] = (4, 4),
        blur_radius: int = 4,
    ) -> None:
        """Draw text with a blurred shadow effect."""
        # Create a temporary image for the shadow
        txt_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
        txt_draw = ImageDraw.Draw(txt_img)

        # Shadow position
        x, y = position
        shadow_pos = (x + offset[0], y + offset[1])

        # Draw the shadow
        txt_draw.text(shadow_pos, text, font=font, fill=shadow_color)
        txt_img = txt_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        # Combine the blurred shadow with the base image
        base_img.alpha_composite(txt_img)

        # Draw the main text on top
        draw = ImageDraw.Draw(base_img)
        draw.text(position, text, font=font, fill=text_color)

    def draw_rounded_rectangle(
        self,
        draw: ImageDraw.Draw,
        bbox: tuple[int, int, int, int],
        radius: int,
        fill_color: tuple[int, int, int, int],
    ) -> None:
        """Draw a rectangle with rounded corners."""
        x1, y1, x2, y2 = bbox

        # Main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill_color)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill_color)

        # Rounded corners
        draw.pieslice(
            [x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill_color
        )
        draw.pieslice(
            [x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill_color
        )
        draw.pieslice(
            [x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill_color
        )
        draw.pieslice(
            [x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill_color
        )

    def draw_time_badge(
        self,
        canvas: Image.Image,
        position: tuple[int, int],
        time_text: str,
        font: ImageFont.FreeTypeFont,
    ) -> None:
        """Draw playtime in a badge/pill shape."""
        x, y = position

        # Create temporary image to measure text
        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        text_bbox = temp_draw.textbbox((0, 0), time_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Badge dimensions with padding
        padding_x = padding_y = 20
        badge_width = text_width + 2 * padding_x
        badge_height = text_height + 2 * padding_y

        # Badge position
        badge_x1 = x
        badge_y1 = y
        badge_x2 = x + badge_width
        badge_y2 = y + badge_height

        # Create overlay for badge with transparency
        overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Draw badge with rounded corners
        radius = 20
        badge_color = (0, 0, 0, 110)  # Semi-transparent black
        self.draw_rounded_rectangle(
            overlay_draw, (badge_x1, badge_y1, badge_x2, badge_y2), radius, badge_color
        )

        # Apply overlay to canvas
        canvas.alpha_composite(overlay)

        # Text position centered in badge
        text_x = x + padding_x
        text_y = y + padding_y - 10

        # Draw text
        draw = ImageDraw.Draw(canvas)
        draw.text((text_x, text_y), time_text, font=font, fill="white")

    def add_played_games(self, canvas: Image.Image, games: List[Game]) -> None:
        """Add played games section to the canvas."""
        y_offset = 350

        for game in games[:3]:  # Show top 3 games
            if game.playtime_2weeks == 0:
                continue

            try:
                game_img = self.download_image(
                    game.appid, "library_600x900.jpg"
                ).resize((200, 300))
            except ImageGenerationError:
                # Skip this game if image can't be downloaded
                continue

            shadow_offset = (8, 8)
            shadow_blur_radius = 20

            # Create shadow image
            shadow_img = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            shadow_x = self.margin + shadow_offset[0]
            shadow_y = y_offset + shadow_offset[1]
            shadow_img.paste(game_img, (shadow_x, shadow_y))

            # Apply blur to shadow
            shadow_img = shadow_img.filter(
                ImageFilter.GaussianBlur(radius=shadow_blur_radius)
            )

            # Composite shadow onto canvas
            canvas.alpha_composite(shadow_img)
            canvas.paste(game_img, (self.margin, y_offset))

            # Smart game name handling (truncate if too long)
            game_name = game.name
            max_chars = 35  # Character limit to avoid overflow
            if len(game_name) > max_chars:
                game_name = game_name[: max_chars - 3] + "..."

            # Format playtime
            hours = game.playtime_2weeks // 60
            minutes = game.playtime_2weeks % 60

            if hours > 0:
                game_time = f"{hours}h {minutes}min"
            else:
                game_time = f"{minutes}min"

            # Text position with better spacing
            text_x = self.margin + 250
            name_y = y_offset + 40
            time_y = y_offset + 120

            # Display game name with pronounced shadow
            self.draw_text_with_blur_shadow(
                canvas,
                (text_x, name_y),
                game_name,
                font=self.font_game,
                text_color="white",
                shadow_color="black",
                offset=(3, 3),
                blur_radius=6,
            )

            # Display playtime in a badge
            self.draw_time_badge(canvas, (text_x, time_y), game_time, self.font_time)

            y_offset += 350

    def create_story_image(
        self, games: List[Game], output_path: str = "steam_story.png"
    ) -> str:
        """Create the complete Steam story image."""
        if not games:
            raise ImageGenerationError("No games provided for image generation")

        try:
            canvas, _ = self.add_background_image(games)
            self.add_header(canvas)
            self.add_played_games(canvas, games)
            canvas = self.add_background_gradient(canvas)
            canvas = self.add_steam_logo(canvas)

            canvas.save(output_path)
            logger.info(f"Steam story image saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to create story image: {e}")
            raise ImageGenerationError(f"Failed to create story image: {e}")


def create_image_service() -> ImageService:
    """Factory function to create image service."""
    return ImageService()
