"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
# Project Modules
from database import DatabaseHandler
from bot import DiscordBot
from server import Server


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    database = DatabaseHandler()
    with open("discord", "r") as fi:
        token = fi.readlines()[0].strip()
    bot = DiscordBot(database)
    server = Server(database, "discord.thrantasquadron.tk", 64731)
    loop.create_task(server.start())
    loop.create_task(bot.bot.start(token))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        database.db.close()
