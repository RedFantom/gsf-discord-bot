"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from ast import literal_eval
import asyncio
from datetime import datetime
from io import BytesIO
import requests
import traceback
# Packages
from dateparser import parse as parse_date
from discord.ext import commands
from discord import User as DiscordUser, Channel, Message
from PIL import Image
# Project Modules
from bot.messages import *
from bot.man import MANUAL
from database import DatabaseHandler, SERVER_NAMES, SERVERS
import parsing.scoreboards as sb
from utils import setup_logger, generate_tag, hash_auth, generate_code
from utils.utils import DATE_FORMAT, TIME_FORMAT, get_temp_file


class DiscordBot(object):
    """
    Run a Discord bot for GSF Parser users. For a list commands, check
    the man.py file.
    """

    PREFIX = "$"
    DESCRIPTION = "A friendly bot to socially interact with GSF " \
                  "statistics and for research"
    CHANNELS = ("general", "code", "bots", "bot", "parser",)
    CHANNELS_ENFORCED = True

    COMMANDS = {
        # Help commands
        "man": ((0, 1), "print_manual"),
        "servers": ((0,), "print_servers"),
        "author": ((0,), "print_author"),
        "privacy": ((0,), "print_privacy"),
        "purpose": ((0,), "print_purpose"),
        "setup": ((0,), "print_setup"),
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
        "results": ((3,), "get_results"),
        # Data Processing
        "scoreboard": ((0, 1), "parse_scoreboard", True),
    }

    PRIVATE = ["forgot_code", "man", "servers", "author", "privacy", "purpose", "setup"]

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
        try:
            author, channel, content = message.author, message.channel, message.content
            if author == self.bot.user:  # Don't process own messages
                return
            if channel.is_private is True:  # Only certain commands allowed
                valid = False
                for command in DiscordBot.PRIVATE:
                    if command in message.content:
                        valid = True
                        break
                if valid is False:
                    await self.bot.send_message(author, NOT_PRIVATE)
                    return
            if channel.name not in DiscordBot.CHANNELS and DiscordBot.CHANNELS_ENFORCED and not channel.is_private:
                self.logger.debug("Ignored a message from wrong channel: {}, channel: {}".format(content, channel.name))
                return
            if self.validate_message(content) is False:
                self.logger.debug("{} is not a command.".format(content))
                return
            command, args = await self.process_command(message)
            if command is None:
                await self.invalid_command(channel, author)
                return
            command = DiscordBot.COMMANDS[command]
            func = self.__getattribute__(command[1])
            mess = command[2] if len(command) == 3 else False
            arguments = (channel, author, args) if not mess else (channel, author, args, message)
            await func(*arguments)
        except Exception as e:
            await self.bot.send_message(message.channel, "That hurt! ```python\n{}```".format(traceback.format_exc()))

    def run(self, token: str):
        """Run the Bot loop"""
        self.bot.run(token)

    async def invalid_command(self, channel: Channel, user: DiscordUser):
        """Send the INVALID_COMMAND message to a user"""
        await self.bot.send_message(channel, INVALID_COMMAND)

    async def print_manual(self, channel: Channel, author: DiscordUser, args: tuple):
        """Send the DiscordBot manual to a channel"""
        if len(args) == 0:
            args = ("commands",)
        command, = args
        await self.bot.send_message(channel, MANUAL[command])

    @staticmethod
    async def get_server_status():
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

    async def print_servers(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send a list of servers to the channel with server statuses"""
        servers = await self.get_server_status()
        if servers is None:
            await self.bot.send_message(channel, "I could not contact the SWTOR website for information.")
            return
        self.logger.debug("Server statuses: {}".format(servers))
        await self.bot.send_message(channel, SERVER_STATUS.format(**servers))

    async def print_author(self, channel: Channel, user: DiscordUser, args: tuple):
        """Print the AUTHOR message"""
        await self.bot.send_message(channel, AUTHOR)

    async def print_privacy(self, channel: Channel, user: DiscordUser, args: tuple):
        await self.bot.send_message(channel, PRIVACY)

    async def print_purpose(self, channel: Channel, user: DiscordUser, args: tuple):
        await self.bot.send_message(channel, PURPOSE)

    async def print_setup(self, channel: Channel, user: DiscordUser, args: tuple):
        await self.bot.send_message(channel, SETUP)

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
        await self.bot.send_message(channel, UPON_REGISTER_PUBLIC)

    async def unregister_user(self, channel: Channel, user: DiscordUser, args: tuple):
        """Remove a user fully from the database"""
        tag = generate_tag(user)
        if self.db.get_user_in_database(tag) is False:
            await self.bot.send_message(channel, NOT_REGISTERED)
            return
        self.db.delete_user(tag)
        self.logger.info("Unregistered {}.".format(tag))
        await self.bot.send_message(channel, UNREGISTER_PUBLIC)
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
            day = datetime.now()
        else:
            day, = args
        day = day.strftime(DATE_FORMAT)
        servers = {server: 0 for server in SERVER_NAMES.keys()}
        servers.update(self.db.get_matches_count_by_day(day))
        message = self.build_string_from_servers(servers)
        message = MATCH_COUNT_DAY.format(day, message)
        await self.bot.send_message(channel, message)

    async def period_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the overview like that of a day for a period"""
        if len(args) == 1:
            args += (datetime.now(),)
        if len(args) != 2:
            await self.bot.send_message(channel, INVALID_ARGS)
            return
        start_s, end_s = args
        start, end = map(lambda e: e.strftime(DATE_FORMAT), args)
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
            day = args[1].strftime(DATE_FORMAT)
        else:
            day = datetime.now().strftime(DATE_FORMAT)
        matches = self.db.get_matches_by_day_by_server(server, day)
        if len(matches) == 0:
            await self.bot.send_message(channel, NO_MATCHES_FOUND)
            return
        message = MATCH_OVERVIEW.format(day, SERVER_NAMES[server], self.build_string_from_matches(matches))
        await self.bot.send_message(channel, message)

    async def get_results(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the list of known results for this match"""
        self.logger.debug("Getting results for {}".format(args))
        server, date, start = args
        date = date.strftime(DATE_FORMAT)
        start = date.strftime(TIME_FORMAT)
        results = self.db.get_match_results(server, date, start)
        self.logger.debug("Results retrieved: {}".format(results))
        if len(results) == 0:
            await self.bot.send_message(channel, NO_RESULTS)
            return
        message = RESULTS.format(start, date, server, self.build_string_from_results(results))
        self.logger.debug(message)
        await self.bot.send_message(channel, message)

    async def parse_scoreboard(self, channel: Channel, user: DiscordUser, args: tuple, message: Message):
        if len(args) == 0:
            args = ("table",)
        type, = args
        if type not in ("table", "excel", "csv",):
            await self.bot.send_message(channel, INVALID_ARGS)
            return
        if len(message.attachments) == 0:
            await self.bot.send_message(channel, "You forgot to include the screenshot.")
            return
        elif len(message.attachments) > 1:
            await self.bot.send_message(channel, "You can only send a single image at a time.")
            return
        link = message.attachments[0]["url"]
        if not link.endswith((".png", ".jpg")):
            await self.bot.send_message(channel, "I only support `png` and `jpg` images, sorry.")
            return
        image = Image.open(BytesIO(requests.get(link).content))
        scale, location = sb.is_scoreboard(image)
        if scale is None or location is None:
            await self.bot.send_message(channel, NOT_A_SCOREBOARD)
            return
        to_edit = await self.bot.send_message(channel, "I'm working on it...")
        results = await sb.parse_scoreboard(image, scale, location, self.bot, to_edit)
        if "table" in args:
            message = "```{}```".format(sb.format_results(results))
            await self.bot.send_message(channel, message)
        else:
            df = sb.results_to_dataframe(results)
            await self.send_dataframe(type, df, channel, user)

    async def send_dataframe(self, type: str, df, channel: Channel, user: DiscordUser):
        if type == "excel":
            path = get_temp_file(ext="xls", user=user)
            sb.write_excel(df, path)
            await self.bot.send_file(channel, path)
        elif type == "csv":
            path = get_temp_file(ext="csv", user=user)
            df.to_csv(path)
            await self.bot.send_file(channel, path)
        else:
            raise ValueError

    @staticmethod
    def validate_message(content: str):
        """Check if this message is a valid command for the bot"""
        return isinstance(content, str) and len(content) > 1 and content[0] == DiscordBot.PREFIX

    async def process_command(self, message: Message):
        """Split the message into command and arguments"""
        content, channel = message.content, message.channel
        elements = content.split(" ")
        command, args = elements[0][1:], elements[1:]
        arguments = list()
        held = str()
        for arg in args:
            if arg.startswith("\"") and not arg.endswith("\""):
                held += arg
                continue
            if arg.endswith("\""):
                held += " " + arg
                self.logger.debug("Processing held command: {}".format(held))
                held = held.replace("\"", "")
                try:
                    held = parse_date(held)
                    if held is None:
                        raise ValueError
                except ValueError:
                    await self.bot.send_message(channel, UNKNOWN_DATE_FORMAT)
                    return None, None
                arguments.append(held)
                held = str()
                continue
            if held != "":
                held += " " + arg
                continue
            date = parse_date(arg)
            arguments.append(arg if date is None else date)
        if command not in DiscordBot.COMMANDS or len(arguments) not in DiscordBot.COMMANDS[command][0]:
            return None, None
        return command, tuple(arguments)

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
        for match in sorted(matches, key=lambda tup: tup[0]):
            start, end, map, score = match
            if end is None:
                end = "Unknown"
            if map is not None:
                match_type, match_map = map.split(",")
            else:
                match_type, match_map = "Unknown", "Unknown"
            if score is not None:
                winner = "Empire" if score > 1.0 else "Republic"
                if winner == "Republic":
                    score = 1 / score
                score = "{:.2f}".format(score)
            else:
                winner, score = "Unknown", "Unknown"
            string += "{:^7}|{:^7}|{:^10}|{:^9}|{:^9}|{:>10}\n".format(
                start, end, match_type, match_map, score, winner)
        return string

    @staticmethod
    def build_string_from_results(results: list):
        """Return a formatted string from a results list"""
        total = str()
        # name, faction, dmgd, dmgt, assists, deaths, ship
        for result in sorted(results, key=lambda item: item[1]):
            string = "{:<16}| {:<9} |{:>10} |{:>10} |{:>12} |{:>7} | {:<14}\n".format(*result)
            total += string
        return total
