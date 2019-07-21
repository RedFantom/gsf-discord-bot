"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
from traceback import format_exc
# Project Modules
from database import DatabaseHandler
from bot.bot import DiscordBot
from server import DiscordServer
from settings import settings
from utils.utils import setup_logger


logger = setup_logger("main", "main.log")


async def run_bot(bot: DiscordBot, token: str):
    """Indefinitely run a DiscordBot"""
    await bot.bot.start(token)
    while bot.bot.is_logged_in:
        if bot.bot.is_closed:
            bot.bot._closed.clear()
            bot.bot.http.recreate()
        try:
            await bot.bot.connect()
        except Exception:
            logger.error(format_exc())
            await asyncio.sleep(60)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    database = DatabaseHandler()
    host, port = settings["server"]["domain"], settings["server"]["port"]
    server = DiscordServer(database, loop, host, port)
    bot = DiscordBot(database, server, loop)
    loop.create_task(server.start())
    loop.create_task(run_bot(bot, settings["discord"]["token"]))
    loop.set_exception_handler(bot.exception_handler)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        database.db.close()
