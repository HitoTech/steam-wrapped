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


def add_played_games(canvas, draw, font_game, games):
    y_offset = 350

    # Créer une police plus petite pour le temps de jeu
    font_time = ImageFont.truetype(Config.FONT_GAME, 45)

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

        # Gestion intelligente du nom du jeu (troncature si trop long)
        game_name = game["name"]
        max_chars = 35  # Limite de caractères pour éviter le débordement
        if len(game_name) > max_chars:
            game_name = game_name[: max_chars - 3] + "..."

            # Formatage du temps simplifié
        total_minutes = game["playtime_2weeks"]
        hours = total_minutes // 60
        minutes = total_minutes % 60

        if hours > 0:
            game_time = f"{hours}h {minutes}min"
        else:
            game_time = f"{minutes}min"

        # Position du texte avec meilleur espacement
        text_x = MARGIN + 250
        name_y = y_offset + 40
        time_y = y_offset + 110

        # Afficher le nom du jeu avec une ombre plus prononcée
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

        # Afficher le temps de jeu avec une couleur légèrement différente
        draw_text_with_blur_shadow(
            canvas,
            (text_x, time_y),
            game_time,
            font=font_time,
            text_color="#E0E0E0",  # Gris clair pour différencier du nom
            shadow_color="black",
            offset=(2, 2),
            blur_radius=4,
        )

        y_offset += 350


def create_story_image(games: list[dict]):
    canvas, draw = add_background_image(games)
    add_header(canvas)
    add_played_games(canvas, draw, font_game, games)
    canvas = add_background_gradient(canvas)
    canvas = add_steam_logo(canvas)

    canvas.save("steam_story.png")
