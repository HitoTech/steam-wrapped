from datetime import datetime, timedelta
from io import BytesIO

import requests
from babel.dates import format_date
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1080, 1920
MARGIN = 60
FONT_TITLE = "fonts/Montserrat-Bold.ttf"
FONT_GAME = "fonts/Montserrat-Regular.ttf"

font_title = ImageFont.truetype(FONT_TITLE, 80)
font_game = ImageFont.truetype(FONT_GAME, 60)


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
    date_text = f"{format_date(start, format='dd/MM', locale='fr_FR')} - {format_date(today, format='dd/MM/yyyy', locale='fr_FR')}"

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
    # Créer une image temporaire pour l'ombre
    txt_img = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)

    # Position de l'ombre
    x, y = position
    shadow_pos = (x + offset[0], y + offset[1])

    # Dessine l’ombre
    txt_draw.text(shadow_pos, text, font=font, fill=shadow_color)
    txt_img = txt_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

    # Combine l'ombre floutée avec l'image de base
    base_img.alpha_composite(txt_img)

    # Dessine le texte principal par-dessus
    draw = ImageDraw.Draw(base_img)
    draw.text(position, text, font=font, fill=text_color)


def add_played_games(canvas, draw, font_game, games):
    y_offset = 300
    for game in games[:3]:
        if game["playtime_2weeks"] == 0:
            continue
        game_img = download_image(game["appid"], "library_600x900.jpg").resize(
            (200, 300)
        )
        border_width = 6
        border_color = "white"

        # Draw a rectangle behind the game logo
        draw.rectangle(
            [
                (MARGIN - border_width, y_offset - border_width),
                (MARGIN + 200 + border_width, y_offset + 300 + border_width),
            ],
            outline=border_color,
            width=border_width,
        )
        canvas.paste(game_img, (MARGIN, y_offset))

        hours = round(game["playtime_2weeks"] / 60, 1)
        draw_text_with_blur_shadow(
            canvas,
            (MARGIN + 250, y_offset + 60),
            f"{game['name']}\n{hours} h",
            font=font_game,
        )
        y_offset += 200


def create_story_image(games: list[dict]):
    canvas, draw = add_background_image(games)
    add_header(canvas)
    add_played_games(canvas, draw, font_game, games)
    canvas = add_background_gradient(canvas)
    canvas = add_steam_logo(canvas)

    canvas.save("steam_story.png")
