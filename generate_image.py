from datetime import datetime, timedelta
from io import BytesIO

import requests
from babel.dates import format_date
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1080, 1920
MARGIN = 60


def download_image(appid: int, format: str) -> Image.Image:
    url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/{format}"
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def add_steam_logo(canvas):
    steam_logo = Image.open("imgs/steam_icon.png").convert("RGBA")
    steam_logo = steam_logo.resize((80, 80))
    canvas.paste(steam_logo, (MARGIN, MARGIN), steam_logo)
    return canvas


def create_story_image(games: list[dict]):
    most_played = max(games, key=lambda g: g["playtime_forever"])
    bg_image = (
        download_image(most_played["appid"], "library_600x900.jpg")
        .resize((WIDTH, HEIGHT))
        .filter(ImageFilter.GaussianBlur(40))
    )

    canvas = Image.new("RGBA", (WIDTH, HEIGHT))
    canvas.paste(bg_image, (0, 0))

    draw = ImageDraw.Draw(canvas)

    # Date en français
    today = datetime.today()
    start = today - timedelta(days=14)
    date_text = f"Du {format_date(start, format='d MMMM', locale='fr_FR')} au {format_date(today, format='d MMMM yyyy', locale='fr_FR')}"

    font_title = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 80)
    font_game = ImageFont.truetype("fonts/Montserrat-Regular.ttf", 60)

    draw.text((MARGIN + 100, MARGIN), "Steam Wrapped", font=font_title, fill="white")
    draw.text((MARGIN, MARGIN + 100), date_text, font=font_game, fill="white")

    y_offset = 300
    for game in games:
        if game["playtime_2weeks"] == 0:
            continue
        game_img = download_image(game["appid"], "library_600x900.jpg").resize(
            (200, 300)
        )
        canvas.paste(game_img, (MARGIN, y_offset))

        hours = round(game["playtime_2weeks"] / 60, 1)
        draw.text(
            (MARGIN + 250, y_offset + 60),
            f"{game['name']}\n{hours} h",
            font=font_game,
            fill="white",
        )
        y_offset += 200

    gradient = Image.new("L", (1, HEIGHT), color=0xFF)
    for y in range(HEIGHT):
        gradient.putpixel(
            (0, y), max(0, min(255, int((y - HEIGHT * 0.4) / (HEIGHT * 0.7) * 255)))
        )

    alpha_gradient = gradient.resize((WIDTH, HEIGHT))
    black_img = Image.new("RGBA", (WIDTH, HEIGHT), color=(0, 0, 0, 255))
    black_img.putalpha(alpha_gradient)
    canvas = Image.alpha_composite(canvas, black_img)

    canvas = add_steam_logo(canvas)

    canvas.save("steam_story.png")
