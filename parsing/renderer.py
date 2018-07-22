"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from os import path
# Packages
from PIL import Image, ImageDraw, ImageFont
# Project Modules
from data.maps import map_dictionary
from parsing.strategies import Phase, Item
from utils.utils import get_assets_directory

RENDER_SIZE = (768, 768)  # Allows for direct rendering
W, H = RENDER_SIZE


def _open_map(phase: Phase)->Image.Image:
    """Open the appropriate map background for a Phase"""
    map_type, map_name = phase.map
    file_name = "{}_{}.jpg".format(map_type, map_dictionary[map_type][map_name])
    file_path = path.join(get_assets_directory(), "maps", file_name)
    image = Image.open(file_path)
    image = image.resize(RENDER_SIZE)
    return image


def _render_item(item: Item, image: Image.Image)->None:
    """Render a single Item onto a Strategy image render"""
    text, font, color = item["name"], item["font"], item["color"]
    coords = int(item["x"] / 768 * W), int(item["y"] / 768 * H)
    draw = ImageDraw.Draw(image)
    font_size = font[1]  # Font Family is shamelessly ignored
    font = ImageFont.FreeTypeFont(size=font_size)
    box = (*coords, *draw.textsize(text, font=font))
    draw.rectangle(box, fill=color)
    draw.text(coords, text, font=font)


def render_phase(phase: Phase) -> Image.Image:
    """Render a Canvas to a PIL image"""
    template = _open_map(phase)
    for name, item in phase:
        _render_item(item, template)
    return template
