"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from io import BytesIO
import random
# Packages
from PIL import Image
import requests
# Project Modules
from data.servers import SERVERS
from data.ships import ship_tier_letters


async def get_server_status():
    """
    Return a dictionary of server statuses

    Downloads the page and parses it by searching for two specific
    patterns:
    - <class="name"> - For the server name - Full server names
    - <class="status"> - For the server status - UP or DOWN
    """
    try:
        page = requests.get("http://www.swtor.com/server-status")
    except (requests.ConnectionError, requests.HTTPError):
        return None
    lines = page.content.decode().split("\n")
    servers = {}
    status = None
    for line in lines:
        if "class=\"name\"" in line:
            server = line.split(">")[1].split("<")[0].lower().replace(" ", "_")
            servers[server] = status
        if "class=\"status\"" in line:
            status = line.split(">")[2].split("<")[0].lower().replace("up", "online").replace("down", "offline")
    for server in SERVERS:
        if server in servers:
            continue
        servers[server] = "offline"
    return servers


async def download_image(link: str)->Image.Image:
    """
    Download file found in the link and return the Image found there

    Asynchronous wrapper around the functions required to download and
    open an Image from a link. Opens the Image by using BytesIO which
    offers the same interface as a file buffer created with open().
    """
    return Image.open(BytesIO(requests.get(link).content))


async def get_random_ship(category: str = None):
    """
    Generate a ship tier string with random category and number

    If category is specified, then only the ship numer is randomly
    generated. Ship tier strings are quite simple: T1S, T2G, etc.
    """
    string = "T{tier}{category}"
    random.seed()
    # Generate random tier
    tier = random.randint(1, 3)
    # Generate category
    if category is None:
        category = random.choice(ship_tier_letters)
    category = category[0].upper()
    # Check if category exists
    if category not in ship_tier_letters:
        return None
    return string.format(tier=tier, category=category)
