"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import os
import asyncio
# Project Modules
from utils import opencv
from utils.utils import get_assets_directory
# Packages
from PIL import Image, ImageFilter
from pytesseract import image_to_string

DEFAULT_WIDTH = 1190
DEFAULT_TABLE_HEIGHT = 430

widths = {
    "name": 280 / DEFAULT_WIDTH,
    "kills": 130 / DEFAULT_WIDTH,
    "assists": 130 / DEFAULT_WIDTH,
    "deaths": 130 / DEFAULT_WIDTH,
    "damage": 130 / DEFAULT_WIDTH,
    "hit": 130 / DEFAULT_WIDTH,
    "objectives": 130 / DEFAULT_WIDTH,
}

digits = ["kills", "assists", "deaths", "damage", "hit", "objectives"]
columns = ["name", "kills", "assists", "deaths", "damage", "hit", "objectives"]

START, END, DIFF = 650, 400, 20
TRAIN_TH = (START + END) // 2
ROWS = 17.2


def dominant_color(image: Image.Image)->tuple:
    """Determine dominant color in image"""
    colors = image.getcolors(image.width * image.height)
    colors = {color: count for count, color in colors}
    return max(colors, key=lambda e: colors[e])


def get_allied(image: Image.Image)->bool:
    """Return whether the row of a player is allied"""
    dom = dominant_color(image)
    return dom[1] > dom[0]


def is_scoreboard(image: Image.Image)->(tuple, None):
    """Use feature matching to check if image contains scoreboard"""
    folder = os.path.join(get_assets_directory(), "headers")
    scales = os.listdir(folder)
    scale, location = None, None
    for file in scales:
        template = Image.open(os.path.join(folder, file))
        is_match, location = opencv.template_match(image, template)
        if not is_match:
            continue
        scale = float(file[:-4])
        break
    if scale is not None:
        return scale, location
    return None, None


def crop_scoreboard(image: Image.Image, scale: float, loc: tuple)->Image.Image:
    """Crop a screenshot to just the scoreboard"""
    template = Image.open(os.path.join(get_assets_directory(), "headers", "{}.png".format(scale)))
    (w, h), (x, y) = template.size, loc
    return image.crop((x, y + h, x + w, y + h + DEFAULT_TABLE_HEIGHT * scale))


def split_scoreboard(image: Image.Image, scale: float, header_loc: tuple)->list:
    """Split a scoreboard into different elements"""
    image = crop_scoreboard(image, scale, header_loc)
    result = list()
    for i in range(16):
        row = (0, i * (image.height / ROWS), image.width, (i + 1) * (image.height / ROWS))
        row_img = image.crop(row)
        row_elems = list()
        for name in columns:
            start = sum([widths[col] * image.width for col in columns[:columns.index(name)]])
            end = start + widths[name]
            crop = (start, 0, end, row_img.height)
            column = row_img.crop(crop)
            column = column.resize((column.width * 3, column.height * 3), Image.LANCZOS)
            row_elems.append(column)
        result.append(row_elems)
    return result


async def perform_ocr(image: Image.Image, is_number: bool)->(str, int, None):
    """Perform OCR on a part of an image"""
    result = None
    for treshold in range(START, END, -DIFF):  # Continue until result is valid
        template = high_pass_invert(image, treshold)
        result = image_to_string(template)
        if is_number and not result.isdigit():  # Try again for numbers
            result = image_to_string(template, config="-psm 10")
        if result == "" or (is_number and not result.isdigit()):
            continue
        break
    if is_number and not result.isdigit():
        template = high_pass_invert(image, START)
        template = template.filter(ImageFilter.GaussianBlur(radius=1))
        result = image_to_string(template)
    if is_number and not result.isdigit():
        result = match_digit(high_pass_invert(image, START))
    if result == "" or (is_number and not result.isdigit()):
        return 0 if is_number else None
    if is_number:
        return int(result)
    return result.replace("\n", "").replace("  ", "")


def match_digit(image: Image.Image)->int:
    """Match the digit in the image to a template in the assets folder"""
    folder = os.path.join(get_assets_directory(), "digits")
    digits = os.listdir(folder)
    results = dict()
    for digit in digits:
        template = Image.open(os.path.join(folder, digit))
        digit = digit[:-4]
        results[digit] = opencv.feature_match(image, template)
    return max(results, key=lambda key: results[key])


def high_pass_invert(image: Image.Image, treshold: int)->Image.Image:
    """Perform a high-pass filter on an image and invert"""
    result = image.copy()  # Do not modify original image
    pixels = result.load()
    for x in range(image.width):
        for y in range(image.height):
            pixel = pixels[x, y]
            if sum(pixel) < treshold:
                pixels[x, y] = (255, 255, 255)
                continue
            pixels[x, y] = (0, 0, 0)
    return result


async def parse_scoreboard(image: Image.Image, scale: float, location: tuple, bot, message)->list:
    """Perform OCR on a screenshot of a scoreboard"""
    split = split_scoreboard(image, scale, location)
    results = list()
    todo, done = sum(len(row) for row in split), 0
    for i, row in enumerate(split):
        text = list()
        for name, column in zip(columns, row):
            result = await perform_ocr(column, name in digits)
            done += 1
            message = await bot.edit_message(message, generate_progress_string(done/todo))
            text.append(result)
        allied = get_allied(column)
        text.append(str(allied))
        results.append(text)
    return results


def format_results(results: list):
    """Print the results in table format"""
    formatter = " {:<22} | {:>5} | {:>7} | {:>6} | {:>6} | {:>3} | {:>10} | {:<6} \n"
    header = formatter.format(*(tuple(column.capitalize() for column in columns) + ("Allied",)))
    separator = "-" * len(header) + "\n"
    string = header + separator
    for player in results:
        string += formatter.format(*tuple(player))
    return string


def generate_progress_string(percent: float):
    return "`[{:<20}] - {:>3}%`".format(int(percent * 20) * "#", int(percent*100))
