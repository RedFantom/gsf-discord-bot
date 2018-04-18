"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
# Project Modules
from database import DatabaseHandler
from bot import DiscordBot


if __name__ == '__main__':
    database = DatabaseHandler()
    with open("discord", "r") as fi:
        token = fi.readlines()[0].strip()
    bot = DiscordBot(database)
    bot.run(token)
