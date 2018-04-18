"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from random import SystemRandom
# Packages
from discord.ext import commands
# Project Modules
from database import DatabaseHandler
from bot import messages
from utils import setup_logger, generate_tag, hash_auth


class DiscordBot(object):
    """Run a Discord bot for GSF Parser users"""

    PREFIX = "$"
    DESCRIPTION = "GSF-Parser based Discord Bot"

    LOWER, UPPER = 100000, 999999

    def __init__(self, database: DatabaseHandler):
        """
        :param database: DatabaseHandler instance
        """
        self.bot = commands.Bot(self.PREFIX, description=self.DESCRIPTION)
        self.db = database
        self.logger = setup_logger("DiscordBot", "bot.log")
        self.setup_commands()

    def setup_commands(self):
        """Create the bot commands"""

        @self.bot.event
        async def on_ready():
            """Callback for log in event"""
            self.logger.debug("Logged in as {}, {}".format(self.bot.user.id, self.bot.user.name))

        @self.bot.command(pass_context=True)
        async def register(context: commands.Context):
            """Register a new Discord User into the server"""
            code = str(SystemRandom().randint(self.LOWER, self.UPPER))
            message = messages.WELCOME.format(code)
            await self.bot.send_message(context.message.author, message)
            self.db.insert_user(generate_tag(context.message.author), hash_auth(code))

    def run(self, token: str):
        """Run the Bot loop"""
        self.bot.run(token)
