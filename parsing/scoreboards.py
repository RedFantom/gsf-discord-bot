"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import os
# Project Modules
from utils import opencv
from utils.utils import get_assets_directory
# Packages
from PIL import Image, ImageFilter
from pytesseract import image_to_string


widths = {
    "name": 280,
    "kills": 130,
    "assists": 130,
    "deaths": 130,
    "damage": 130,
    "hit": 130,
    "objectives": 130,
}

digits = ["kills", "assists", "deaths", "damage", "hit", "objectives"]
columns = ["name", "kills", "assists", "deaths", "damage", "hit", "objectives"]

START, END, DIFF = 650, 580, 10
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


def is_scoreboard(image: Image.Image)->bool:
    """Use feature matching to check if image contains scoreboard"""
    template = Image.open(os.path.join(get_assets_directory(), "table_bar.png"))
    result = opencv.feature_match(image, template)
    return True


def crop_scoreboard(image: Image.Image)->Image.Image:
    """Crop a screenshot to just the scoreboard"""
    w, h = image.width, image.height
    xc, yc = w / 2, h / 2
    crop = (xc - 600, yc - 170, xc + 600, yc + 260)
    return image.crop(crop)


def split_scoreboard(image: Image.Image)->list:
    """Split a scoreboard into different elements"""
    image = crop_scoreboard(image)
    result = list()
    for i in range(16):
        row = (0, i * (image.height / ROWS), image.width, (i + 1) * (image.height / ROWS))
        row_img = image.crop(row)
        row_elems = list()
        for name in columns:
            start = sum([widths[col] for col in columns[:columns.index(name)]])
            end = start + widths[name]
            crop = (start, 0, end, row_img.height)
            column = row_img.crop(crop)
            column = column.resize((column.width * 3, column.height * 3), Image.LANCZOS)
            row_elems.append(column)
        result.append(row_elems)
    return result


def perform_ocr(image: Image.Image, is_number: bool)->(str, int, None):
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
    return result


def match_digit(image: Image.Image)->int:
    """Match the digit in the image to a template in the assets folder"""
    folder = "../assets/digits"
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


def parse_scoreboard(image: Image.Image)->list:
    """Perform OCR on a screenshot of a scoreboard"""
    split = split_scoreboard(image)
    results = list()
    for i, row in enumerate(split):
        text = list()
        for name, column in zip(columns, row):
            result = perform_ocr(column, name in digits)
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


if __name__ == "__main__":
    Image.open("../assets/tests/test2.jpg").convert("RGBA").save("../assets/tests/test2.png")
    results = parse_scoreboard(Image.open("../assets/tests/test2.png"))
    print(format_results(results))
