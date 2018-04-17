"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
from utils.utils import \
    setup_logger, \
    datetime_to_str, str_to_date, str_to_time, \
    hash_auth
from utils.discord import generate_tag, generate_code

UNKNOWN_MAP = "Unknown"
UNKNOWN_END = "-"
UNKNOWN_SCORE = 0.0

MAP_NAMES = {
    "io": "Battle over Iokath",
    "km": "Kuat Mesas",
    "ls": "Lost Shipyards",
    "de": "Denon Exosphere",
}
