"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
# Packages
from discord.ext import commands
from discord import User as DiscordUser, Channel
# Project Modules
from database import DatabaseHandler
from bot import messages
from utils import setup_logger, generate_tag, hash_auth, generate_code


class DiscordBot(object):
    """Run a Discord bot for GSF Parser users"""

    PREFIX = "$"
    DESCRIPTION = "GSF-Parser based Discord Bot"

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
            self.register_user(context.message.author, context.message.channel)

        @self.bot.command(pass_context=True)
        async def forgot_code(context: commands.Context):
            """Request a new authentication code from the server"""
            self.forgot_code(context.message.author, context.message.channel)

    def run(self, token: str):
        """Run the Bot loop"""
        self.bot.run(token)

    async def register_user(self, user: DiscordUser, channel: Channel):
        """Register a new user into the database"""
        tag = generate_tag(user)
        if self.db.get_auth_code(tag) is not None:
            self.bot.send_message(channel, messages.ALREADY_REGISTERED)
            return
        code = generate_code()
        message = messages.UPON_REGISTER.format(code)
        await self.bot.send_message(user, message)
        self.logger.info("Registering new user {}.".format(tag))
        self.db.insert_user(generate_tag(user), hash_auth(code))
        self.bot.send_message(channel, messages.UPON_REGISTER_PUBLIC.format(user))

    async def forgot_code(self, user: DiscordUser, channel: Channel):
        """Generate a new access code for the user"""
        tag = generate_tag(user)
        if self.db.get_auth_code(tag) is None:
            self.bot.send_message(channel, messages.NOT_REGISTERED.format(user))
            return
        self.logger.info("Generating new access code for {}.".format(tag))
        code = generate_code()
        self.db.update_auth_code(tag, code)
        self.bot.send_message(user, messages.NEW_CODE.format(code))
