from datetime import datetime, timedelta
from io import BytesIO

import requests
from babel.dates import format_date
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from config import Config

WIDTH, HEIGHT = Config.IMAGE_WIDTH, Config.IMAGE_HEIGHT
MARGIN = 60

font_title = ImageFont.truetype(Config.FONT_TITLE, 80)
font_game = ImageFont.truetype(Config.FONT_GAME, 60)


def download_image(appid: int, format: str) -> Image.Image:
    url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/{format}"
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def add_background_image(games):
    most_played = max(games, key=lambda g: g["playtime_forever"])
    bg_image = (
        download_image(most_played["appid"], "library_600x900.jpg")
        .resize((WIDTH, HEIGHT))
        .filter(ImageFilter.GaussianBlur(40))
    )
    canvas = Image.new("RGBA", (WIDTH, HEIGHT))
    canvas.paste(bg_image, (0, 0))
    draw = ImageDraw.Draw(canvas)
    return canvas, draw


def add_header(canvas):
    today = datetime.today()
    start = today - timedelta(days=14)
    date_text = f"{format_date(start, format='dd MMMM', locale=Config.LOCALE)} - {format_date(today, format='dd MMMM yyyy', locale=Config.LOCALE)}"

    banner_height = 220
    banner_rect = [(0, 0), (WIDTH, MARGIN + banner_height)]

    # Create a semi-transparent black rectangle
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(banner_rect, fill=(0, 0, 0, 120))  # Black with transparency
    canvas.alpha_composite(overlay)

    draw_text_with_blur_shadow(
        canvas, (MARGIN + 100, MARGIN), "Steam Wrapped", font_title
    )
    draw_text_with_blur_shadow(canvas, (MARGIN, MARGIN + 100), date_text, font_game)


def add_steam_logo(canvas):
    steam_logo = Image.open("imgs/steam_icon.png").convert("RGBA")
    steam_logo = steam_logo.resize((80, 80))
    canvas.paste(steam_logo, (MARGIN, MARGIN), steam_logo)
    return canvas


def add_background_gradient(canvas):
    gradient = Image.new("L", (1, HEIGHT), color=0xFF)
    for y in range(HEIGHT):
        gradient.putpixel(
            (0, y), max(0, min(255, int((y - HEIGHT * 0.4) / (HEIGHT * 0.7) * 255)))
        )

    alpha_gradient = gradient.resize((WIDTH, HEIGHT))
    black_img = Image.new("RGBA", (WIDTH, HEIGHT), color=(0, 0, 0, 255))
    black_img.putalpha(alpha_gradient)
    canvas = Image.alpha_composite(canvas, black_img)
    return canvas


def draw_text_with_blur_shadow(
    base_img,
    position,
    text,
    font,
    text_color="white",
    shadow_color="black",
    offset=(4, 4),
    blur_radius=4,
):
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


def draw_rounded_rectangle(draw, bbox, radius, fill_color):
    """Draw a rectangle with rounded corners"""
    x1, y1, x2, y2 = bbox

    # Main rectangle
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill_color)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill_color)

    # Rounded corners
    draw.pieslice([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=fill_color)
    draw.pieslice([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=fill_color)
    draw.pieslice([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=fill_color)
    draw.pieslice([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=fill_color)


def draw_time_badge(canvas, position, time_text, font):
    """Draw playtime in a badge/pill shape"""
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
    draw_rounded_rectangle(
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


def add_played_games(canvas, font_game, games):
    y_offset = 350

    # Create smaller font for playtime
    font_time = ImageFont.truetype(Config.FONT_GAME, 40)

    for game in games[:3]:
        if game["playtime_2weeks"] == 0:
            continue
        game_img = download_image(game["appid"], "library_600x900.jpg").resize(
            (200, 300)
        )

        shadow_offset = (8, 8)
        shadow_blur_radius = 20

        # Create shadow image
        shadow_img = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow_x = MARGIN + shadow_offset[0]
        shadow_y = y_offset + shadow_offset[1]
        shadow_img.paste(game_img, (shadow_x, shadow_y))

        # Apply blur to shadow
        shadow_img = shadow_img.filter(
            ImageFilter.GaussianBlur(radius=shadow_blur_radius)
        )

        # Composite shadow onto canvas
        canvas.alpha_composite(shadow_img)
        canvas.paste(game_img, (MARGIN, y_offset))

        # Smart game name handling (truncate if too long)
        game_name = game["name"]
        max_chars = 35  # Character limit to avoid overflow
        if len(game_name) > max_chars:
            game_name = game_name[: max_chars - 3] + "..."

        # Simplified time formatting
        total_minutes = game["playtime_2weeks"]
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            game_time = f"{hours}h {minutes}min"
        else:
            game_time = f"{minutes}min"

        # Text position with better spacing
        text_x = MARGIN + 250
        name_y = y_offset + 40
        time_y = y_offset + 120

        # Display game name with pronounced shadow
        draw_text_with_blur_shadow(
            canvas,
            (text_x, name_y),
            game_name,
            font=font_game,
            text_color="white",
            shadow_color="black",
            offset=(3, 3),
            blur_radius=6,
        )

        # Display playtime in a badge
        draw_time_badge(canvas, (text_x, time_y), game_time, font_time)

        y_offset += 350


def create_story_image(games: list[dict]):
    canvas, draw = add_background_image(games)
    add_header(canvas)
    add_played_games(canvas, font_game, games)
    canvas = add_background_gradient(canvas)
    canvas = add_steam_logo(canvas)

    canvas.save("steam_story.png")
