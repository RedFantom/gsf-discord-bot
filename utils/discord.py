"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
from discord import User


def generate_tag(user: User)->str:
    """Return a Discord string tag for the given user"""
    name = user.name
    number = user.discriminator
    if isinstance(number, str) and number[0] == "#":
        number = int(number[1:])
    return "@{}#{}".format(name, number)
