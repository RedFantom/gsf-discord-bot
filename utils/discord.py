"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from random import SystemRandom
# Packages
from discord import User


LOWER, UPPER = 100000, 999999


def generate_tag(user: User)->str:
    """Return a Discord string tag for the given user"""
    name = user.name
    number = user.discriminator
    if isinstance(number, str) and number[0] == "#":
        number = int(number[1:])
    return "@{}#{}".format(name, number)


def generate_code():
    """Return a cryptographically random 6-digit code"""
    return SystemRandom().randint(LOWER, UPPER)
