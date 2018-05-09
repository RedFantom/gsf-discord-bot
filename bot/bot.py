"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
from datetime import datetime, timedelta
import traceback
# Packages
from dateparser import parse as parse_date
from discord.ext import commands
from discord import User as DiscordUser, Channel, Message
# Project Modules
from bot.func import *
from bot.strings import *
from bot.messages import *
from bot.static import *
from bot.man import MANUAL
from database import DatabaseHandler, SERVER_NAMES
from parsing import scoreboards as sb
from server.discord import DiscordServer
from utils import setup_logger, generate_tag, hash_auth, generate_code
from utils import UNKNOWN_END, UNKNOWN_MAP, MAP_NAMES
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

    OVERVIEW_CHANNELS = ("matches",)

    IMAGE_TYPES = ("png", "jpg", "bmp")

    COMMANDS = {
        # Help commands
        "man": ((0, 1), "print_manual"),
        "servers": ((0,), "print_servers"),
        "author": ((0,), "print_author"),
        "privacy": ((0,), "print_privacy"),
        "purpose": ((0,), "print_purpose"),
        "setup": ((0,), "print_setup"),
        "help": ((0,), "print_help"),
        "link": ((0,), "print_link"),
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

    PRIVATE = [
        "forgot_code", "man", "servers", "author", "privacy", "purpose", "setup", "link", "help"
    ]

    def __init__(self, database: DatabaseHandler, server: DiscordServer, loop: asyncio.BaseEventLoop):
        """
        :param database: DatabaseHandler instance
        """
        self.bot = commands.Bot(self.PREFIX, description=self.DESCRIPTION)
        self.db = database
        self.logger = setup_logger("DiscordBot", "bot.log")
        self.setup_commands()
        self.server = server
        self.overview_messages = dict()
        self.loop = loop
        self.loop.create_task(self.server_status_monitor())
        self.loop.create_task(self.matches_monitor())

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

    async def server_status_monitor(self):
        """
        Monitor the server status and send a message upon changes

        This runs as a coroutine, continuously monitoring the status of
        each server and sending a message to all available channels if
        the server status changes.
        """
        statuses = dict()
        messages = list()
        while True:
            servers = await get_server_status()
            for server, status in servers.items():
                if server not in statuses:
                    statuses[server] = "online"
                if status == statuses[server]:
                    continue
                messages.append(locals()["SERVER_{}".format(status)].format(server))
            for message in messages:
                for channel in self.validated_channels:
                    await self.bot.send_message(channel, message)
            await asyncio.sleep(60)

    async def matches_monitor(self):
        """
        Monitor the matches running on each server

        This runs as a coroutine, continuously monitoring the running
        matches on each server by receiving data from
        """
        while True:
            try:
                matches = self.server.matches.copy()
                rows = list()
                now = datetime.now()
                for (server, start, map, score, end) in matches.values():
                    server = SERVER_NAMES[server]
                    running = end == UNKNOWN_END
                    strptime = datetime.strptime
                    if running is True:
                        time = (now - datetime.combine(now.date(), strptime(start, TIME_FORMAT).time()))
                    else:
                        time = (strptime(end, TIME_FORMAT) - strptime(start, TIME_FORMAT))
                    time = int(time.total_seconds())
                    state = "active" if running is True else "done"
                    if map == UNKNOWN_MAP:
                        type = "..."
                    else:
                        type, map = map.split(",")
                        map = MAP_NAMES[map]
                        type = type.upper()
                    score = float(score)
                    if score > 1.0:
                        score = 1 / score
                        faction = "e"
                    else:
                        faction = "r"
                    rows.append(MATCHES_ROW.format(state, server, type, map, score, faction, divmod(time, 60)[0]))
                row_message = str()
                for row in rows:
                    row_message += row
                message = MATCHES_TABLE.format(row_message, now.strftime("%H:%m:%S"))
                rows.clear()
                for channel in self.overview_channels:
                    if channel in self.overview_messages:
                        await self.bot.edit_message(self.overview_messages[channel], message)
                        continue
                    self.overview_messages[channel] = await self.bot.send_message(channel, message)
            except Exception:
                self.logger.error("An error occurred while building the overview message:\n{}".
                                  format(traceback.format_exc()))
            await asyncio.sleep(30)

    @property
    def validated_channels(self)->list:
        """Generator for all valid channels this Bot is in"""
        channels = list()
        for server in self.bot.servers:
            for channel in server.channels:
                if self.validate_channel(channel) is False:
                    continue
                channels.append(channel)
        return channels

    @property
    def overview_channels(self)->list:
        channels = list()
        for server in self.bot.servers:
            for channel in server.channels:
                if channel.name not in self.OVERVIEW_CHANNELS:
                    continue
                channels.append(channel)
        return channels

    async def invalid_command(self, channel: Channel, user: DiscordUser):
        """Send the INVALID_COMMAND message to a user"""
        await self.bot.send_message(channel, INVALID_COMMAND)

    async def print_manual(self, channel: Channel, author: DiscordUser, args: tuple):
        """Send the DiscordBot manual to a channel"""
        if len(args) == 0:
            args = ("commands",)
        command, = args
        await self.bot.send_message(channel, MANUAL[command])

    async def print_help(self, channel: Channel, user: DiscordUser, args: tuple):
        """Print the HELP message"""
        await self.bot.send_message(channel, HELP)

    async def print_servers(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send a list of servers to the channel with server statuses"""
        servers = await get_server_status()
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

    async def print_link(self, channel: Channel, user: DiscordUser, args: tuple):
        links = await get_download_link()
        if links is None:
            await self.bot.send_message(channel, GITHUB_RATE_LIMIT)
            return
        await self.bot.send_message(channel, GITHUB_DOWNLOAD_LINK.format(*links))

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
        message = build_string_from_servers(servers)
        message = MATCH_COUNT_DAY.format(day, message)
        await self.bot.send_message(channel, message)

    async def period_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the overview like that of a day for a period"""
        if len(args) == 1:
            args += (datetime.now(),)
        start, end = args
        start_s, end_s = map(lambda dt: dt.strftime(DATE_FORMAT), (start, end))
        if end <= start:
            await self.bot.send_message(channel, INVALID_DATE_RANGE)
            return
        servers = self.db.get_matches_count_by_period(start, end)
        message = build_string_from_servers(servers)
        message = MATCH_COUNT_PERIOD.format(start_s, end_s, message)
        await self.bot.send_message(channel, message)

    async def week_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the overview like that of a day for the last week"""
        servers = self.db.get_matches_count_by_week()
        message = build_string_from_servers(servers)
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
        message = MATCH_OVERVIEW.format(day, SERVER_NAMES[server], build_string_from_matches(matches))
        await self.bot.send_message(channel, message)

    async def get_results(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send the list of known results for this match"""
        self.logger.debug("Getting results for {}".format(args))
        server, date, start = args
        date = date.strftime(DATE_FORMAT)
        start = start.strftime(TIME_FORMAT)
        results = self.db.get_match_results(server, date, start)
        self.logger.debug("Results retrieved: {}".format(results))
        if len(results) == 0:
            await self.bot.send_message(channel, NO_RESULTS)
            return
        message = RESULTS.format(start, date, server, build_string_from_results(results))
        self.logger.debug(message)
        await self.bot.send_message(channel, message)

    async def parse_scoreboard(self, channel: Channel, user: DiscordUser, args: tuple, message: Message):
        """
        Parse a scoreboard with OCR on user request

        Downloads the image attached to the message by the user and then
        parses it using the functions in scoreboards.py to generate
        either a string table or a file.
        """
        if len(args) == 0:
            args = ("table",)
        type, = args
        if type not in ("table", "excel", "csv",):
            await self.bot.send_message(channel, INVALID_ARGS)
            return
        images = await self.get_images(message)
        for name, image in images.items():
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
        """
        Send a Pandas DataFrame instance as a file to a channel
        :param type: File type in ("excel", "csv")
        :param df: DataFrame instance to send
        :param channel: Channel to send the file to
        :param user: User that requested the file conversion
        """
        if type == "excel":
            path = get_temp_file(ext="xls", user=user)
            sb.write_excel(df, path)
        elif type == "csv":
            path = get_temp_file(ext="csv", user=user)
            df.to_csv(path)
        else:
            self.logger.error("Invalid scoreboard parsing type: {}".format(type))
            return None
        await self.bot.send_file(channel, path)

    async def get_images(self, message: Message, to_edit: Message=None)->dict:
        """
        Download and return a list of Image objects from the attachments

        First downloads the images from the Discord CDN and then
        converts them into Image instances. Then returns a dictionary
        of filename: Image.
        """
        todo = len(message.attachments)
        done = 1
        if to_edit is not None:
            to_edit = await self.bot.edit_message(to_edit, DOWNLOADING_IMAGES.format(done, todo))
        channel = message.channel
        results = dict()
        for attachment in message.attachments:
            if to_edit is not None:
                to_edit = await self.bot.edit_message(to_edit, DOWNLOADING_IMAGES.format(done, todo))
            link, name = attachment["url"], attachment["filename"]
            done += 1
            if not name.endswith(DiscordBot.IMAGE_TYPES):
                await self.bot.send_message(channel, UNSUPPORTED_IMAGE_TYPE.format(name))
                continue
            results[name] = await download_image(link)
        return results

    @staticmethod
    def validate_message(content: str):
        """Check if this message is a valid command for the bot"""
        return isinstance(content, str) and len(content) > 1 and content[0] == DiscordBot.PREFIX

    @staticmethod
    def validate_channel(channel: Channel):
        """Check if this message was sent in a valid channel for the Bot"""
        return not (channel.name not in DiscordBot.CHANNELS and DiscordBot.CHANNELS_ENFORCED and not channel.is_private)

    async def process_command(self, message: Message):
        """Split the message into command and arguments"""
        content, channel = message.content, message.channel
        elements = content.split(" ")
        command, args = elements[0][len(self.PREFIX):], elements[1:]
        arguments = await self.parse_arguments(args, channel)
        if command not in DiscordBot.COMMANDS or len(arguments) not in DiscordBot.COMMANDS[command][0]:
            return None, None
        return command, tuple(arguments)

    async def parse_arguments(self, args: tuple, channel: Channel)->list:
        """
        Parse the arguments given in a command to a list of real
        arguments. Uses dateparser.parse function to support many
        different date and time formats.
        :param args: A tuple of str arguments
        :param channel: Channel the command was given in
        :return: list or arguments
        """
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
                    if isinstance(held, timedelta):
                        held = datetime.now() - held
                except ValueError:
                    await self.bot.send_message(channel, UNKNOWN_DATE_FORMAT)
                    return list()
                arguments.append(held)
                held = str()
                continue
            if held != "":
                held += " " + arg
                continue
            date = parse_date(arg)
            arguments.append(arg if date is None else date)
        return arguments
