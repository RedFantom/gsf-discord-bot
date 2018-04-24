"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import requests
from datetime import datetime
from ast import literal_eval
# Packages
from discord.ext import commands
from discord import User as DiscordUser, Channel, Message
# Project Modules
from database import DatabaseHandler, SERVERS, SERVER_NAMES
from bot.messages import *
from utils import setup_logger, generate_tag, hash_auth, generate_code
from utils.utils import DATE_FORMAT


class DiscordBot(object):
    """
    Run a Discord bot for GSF Parser users. Discord Bot commands:

    :register: Register a new user to the Discord bot. Sends a unique
        registration code to the user who issued the command.

    :forgot_code: Generate a new access code for the user and send it
        through PM. Invalidates the old access code.

    :overview {type}: Send a public message into the channel where the
        user issued the command, tagging the user for notification.

        :user {name} {day}: Display the results of this user for each
            match played on a given day. If day is not given, then
            today is assumed.
        :day {date} {server}:
        :week: Display the amount of matches per server for the last
            seven days
        :period {start} {end}:
        :server:

    :unregister: Remove the user who issued the command fully from the
        whole database, deleting all information referencing the user.
    """

    PREFIX = "$"
    DESCRIPTION = "GSF-Parser based Discord Bot"
    CHANNELS = ("general",)

    COMMANDS = {
        # Help commands
        "manual": ((0,), "print_manual"),
        "servers": ((0,), "print_servers"),
        # User Commands
        "register": ((0,), "register_user"),
        "unregister": ((0,), "unregister_user"),
        "forgot_code": ((0,), "forgot_code"),
        # Data Retrieval
        "period": ((1, 2), "period_overview"),
        "day": ((0, 1), "day_overview"),
        "week": ((0,), "week_overview"),
        "matches": ((1, 2), "matches_overview"),
        "character": ((2, 3), "find_character_owner"),
    }

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

        @self.bot.event
        async def on_message(message: Message):
            """Process a given message"""
            await self.on_message(message)

    async def on_message(self, message: Message):
        """
        Process a message in the channel the bot has access to. Only
        messages starting with the command prefix are processed. The
        amount of arguments is checked, and then the command is
        executed.
        """
        author, channel, content = message.author, message.channel, message.content
        if author == self.bot.user:
            return
        if not isinstance(author, DiscordUser) or not isinstance(channel, Channel):
            self.logger.error("Invalid types: {}, {}".format(author, channel))
            return
        if channel.name not in DiscordBot.CHANNELS:
            self.logger.debug("Ignored a message from wrong channel: {}, channel: {}".format(content, channel.name))
            return
        if self.validate_message(content) is False:
            self.logger.debug("{} is not a command.".format(content))
            return
        command, args = self.process_command(content)
        if command is None:
            await self.invalid_command(channel, author)
            return
        func = self.__getattribute__(DiscordBot.COMMANDS[command][1])
        await func(channel, author, args)

    def run(self, token: str):
        """Run the Bot loop"""
        self.bot.run(token)

    async def invalid_command(self, channel: Channel, user: DiscordUser):
        """Send the INVALID_COMMAND message to a user"""
        await self.bot.send_message(channel, INVALID_COMMAND.format(user.mention))

    async def print_manual(self, channel: Channel, author: DiscordUser, args: tuple):
        """Send the DiscordBot manual to a channel"""
        await self.bot.send_message(channel, MANUAL)

    async def print_servers(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send a list of servers to the channel with server statuses"""
        try:
            page = requests.get("http://www.swtor.com/server-status")
        except (requests.ConnectionError, requests.HTTPError):
            self.bot.send_message(channel, "I could not contact the SWTOR website for information.")
            return
        self.bot.send_typing(channel)
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
        self.logger.debug("Server statuses: {}".format(servers))
        await self.bot.send_message(channel, SERVERS.format(**servers))

    """User Commands"""

    async def register_user(self, channel: Channel,  user: DiscordUser, args: tuple):
        """Register a new user into the database"""
        tag = generate_tag(user)
        self.logger.debug("Initializing registration of a user: {}".format(tag))
        if self.db.get_auth_code(tag) is not None:
            await self.bot.send_message(channel, ALREADY_REGISTERED)
            self.logger.debug("{} is already registered.".format(tag))
            return
        code = generate_code()
        message = UPON_REGISTER.format(code)
        self.logger.debug("Sending registration message to {}.".format(tag))
        await self.bot.send_message(user, message)
        self.logger.info("Registering new user {}.".format(tag))
        self.db.insert_user(generate_tag(user), hash_auth(code))
        self.logger.debug("Sending public registration message to {}.".format(channel.name))
        await self.bot.send_message(channel, UPON_REGISTER_PUBLIC.format(user.mention))

    async def unregister_user(self, channel: Channel, user: DiscordUser, args: tuple):
        """Remove a user fully from the database"""
        tag = generate_tag(user)
        if self.db.get_user_in_database(tag) is False:
            await self.bot.send_message(channel, NOT_REGISTERED.format(user.mention))
            return
        self.db.delete_user(tag)
        self.logger.info("Unregistered {}.".format(tag))
        await self.bot.send_message(channel, UNREGISTER_PUBLIC.format(user.mention))
        await self.bot.send_message(user, UNREGISTER)

    async def forgot_code(self, channel: Channel, user: DiscordUser, args: tuple):
        """Generate a new access code for the user"""
        tag = generate_tag(user)
        if self.db.get_auth_code(tag) is None:
            await self.bot.send_message(channel, NOT_REGISTERED.format(user))
            return
        self.logger.info("Generating new access code for {}.".format(tag))
        code = generate_code()
        self.db.update_auth_code(tag, code)
        await self.bot.send_message(user, NEW_CODE.format(code))

    """Data Retrieval"""

    async def day_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send an overview for a specific day"""
        if len(args) == 0:
            day = datetime.now().strftime(DATE_FORMAT)
        else:
            day, = args
            try:
                datetime.strptime(day, DATE_FORMAT)
            except ValueError:
                await self.bot.send_message(channel, UNKNOWN_DATE_FORMAT)
                return
        servers = {server: 0 for server in SERVER_NAMES.keys()}
        servers.update(self.db.get_matches_count_by_day(day))
        message = self.build_string_from_servers(servers)
        message = MATCH_COUNT_DAY.format(day, message)
        await self.bot.send_message(channel, message)

    async def period_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the overview like that of a day for a period"""
        self.bot.send_typing(channel)
        if len(args) == 1:
            args += (datetime.now().strftime(DATE_FORMAT),)
        if len(args) != 2:
            await self.bot.send_message(channel, INVALID_ARGS)
            return
        start, end = start_s, end_s = args
        try:
            start, end = map(lambda s: datetime.strptime(s, DATE_FORMAT), (start, end))
        except ValueError:
            await self.bot.send_message(channel, UNKNOWN_DATE_FORMAT)
            return
        if end <= start:
            await self.bot.send_message(channel, INVALID_DATE_RANGE)
            return
        servers = self.db.get_matches_count_by_period(start, end)
        message = self.build_string_from_servers(servers)
        message = MATCH_COUNT_PERIOD.format(start_s, end_s, message)
        await self.bot.send_message(channel, message)

    async def week_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the overview like that of a day for the last week"""
        servers = self.db.get_matches_count_by_week()
        message = self.build_string_from_servers(servers)
        await self.bot.send_message(channel, MATCH_COUNT_WEEK.format(message))

    async def find_character_owner(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the owner of a character to the channel"""
        server = args[0]
        server = server.upper()
        if server not in SERVER_NAMES.keys():
            await self.bot.send_message(channel, INVALID_SERVER)
            return
        if len(args[1:]) == 2:
            name = "{} {}".format(*args[1:])
        else:
            name = args[1]
        owner = self.db.get_character_owner(server, name)
        if owner is None:
            await self.bot.send_message(channel, UNKNOWN_CHARACTER.format(name, SERVER_NAMES[server]))
            return
        await self.bot.send_message(channel, CHARACTER_OWNER.format(owner))

    async def matches_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send an overview of matches for a given server"""
        server = args[0]
        if server not in SERVER_NAMES.keys():
            await self.bot.send_message(channel, INVALID_SERVER)
            return
        if len(args) == 2:
            day = args[1]
            try:
                datetime.strptime(day, DATE_FORMAT)
            except ValueError:
                await self.bot.send_message(channel, UNKNOWN_DATE_FORMAT)
                return
        else:
            day = datetime.now().strftime(DATE_FORMAT)
        matches = self.db.get_matches_by_day_by_server(server, day)
        if len(matches) == 0:
            await self.bot.send_message(channel, NO_MATCHES_FOUND)
            return
        message = MATCH_OVERVIEW.format(day, SERVER_NAMES[server], self.build_string_from_matches(matches))
        await self.bot.send_message(channel, message)

    @staticmethod
    def validate_message(content: str):
        """Check if this message is a valid command for the bot"""
        return isinstance(content, str) and len(content) > 1 and content[0] == DiscordBot.PREFIX

    @staticmethod
    def process_command(content: str):
        """Split the message into command and arguments"""
        elements = content.split(" ")
        command, args = elements[0][1:], elements[1:]
        if command not in DiscordBot.COMMANDS or len(args) not in DiscordBot.COMMANDS[command][0]:
            return None, None
        return command, args

    @staticmethod
    def build_string_from_servers(servers: dict):
        """Return a formatted string from a server: match_count dict"""
        message = str()
        for server, count in servers.items():
            message += "{}: {}\n".format(SERVER_NAMES[server], count)
        return message

    @staticmethod
    def build_string_from_matches(matches: list):
        """Return a formatted string from a matches list"""
        string = str()
        for match in matches:
            start, end, map, score = match
            if end is None:
                end = "Uknown"
            if map is not None:
                match_type, match_map = literal_eval(map)
            else:
                match_type, match_map = "Unknown", "Unknown"
            if score is not None:
                imp, rep = map(int, score.split("-"))
                if imp > rep:
                    winner = "Empire"
                elif imp == rep:
                    winner = "Close call",
                else:
                    winner = "Republic"
            else:
                winner, score = "Uknown", "Uknown"
            string += "{:^7}|{:^7}|{:^10}|{:^9}\n".format(  # |{:^9}|{:^10}\n".format(
                start, end, match_type, match_map)  # , score, winner)
        return string
