"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
from typing import *
import traceback
# Packages
from dateparser import parse as parse_date
import discord
from discord.ext import commands
from discord import User as DiscordUser, Channel, Message, Embed
from raven import Client as RavenClient
# Project Modules
from bot.func import *
from bot.strings import *
from bot.messages import *
from data.servers import SERVER_NAMES
from data.maps import map_names
from database import DatabaseHandler
from parsing import scoreboards as sb
from parsing.renderer import render_phase
from parsing.ships import Ship
from parsing.strategies import Strategy
from server.discord import DiscordServer
from utils import setup_logger, generate_tag
from utils.utils import DATE_FORMAT, TIME_FORMAT, get_temp_file


class DiscordBot(object):
    """
    Run a Discord bot for GSF Parser users. For a list commands, check
    the man.py file.
    """

    PREFIX = "$"
    DESCRIPTION = "A friendly bot to socially interact with GSF " \
                  "statistics and for research"
    CHANNELS = ("general", "code", "bots", "bot", "parser", "exceptions")
    CHANNELS_ENFORCED = True

    OVERVIEW_CHANNELS = ("matches",)

    IMAGE_TYPES = ("png", "jpg", "bmp")

    COMMANDS = {
        # Help commands
        "man": ((0, 1), "print.manual"),
        "servers": ((0,), "print.servers"),
        "author": ((0,), "print.author"),
        "privacy": ((0,), "print.privacy"),
        "purpose": ((0,), "print.purpose"),
        "setup": ((0,), "print.setup"),
        "help": ((0,), "print.help"),
        "link": ((0,), "print.link"),
        # User Commands
        "register": ((0,), "user.register"),
        "unregister": ((0,), "user.unregister"),
        "forgot_code": ((0,), "user.forgot_code"),
        # Data Retrieval
        "period": ((1, 2), "overview.period"),
        "day": ((0, 1), "overview.day"),
        "week": ((0,), "overview.week"),
        "matches": ((1, 2), "overview.matches"),
        "character": ((2, 3), "find_character_owner"),
        "results": ((3,), "get_results"),
        "random": ((0, 1), "random_ship"),
        "strategy": ((0, 1, 2, 3), "strategy"),
        # Data Processing
        "scoreboard": ((0, 1), "parse_scoreboard", True),
        "build": (range(2, 20), "build.calculator"),
        "event": ((1, 2), "event", True),
    }

    DATES = {
        "period": (True, True),
        "day": (True,),
        "matches": (False, True),
        "results": (False, True, True),
    }

    PRIVATE = [
        "forgot_code",
        "man",
        "servers",
        "author",
        "privacy",
        "purpose",
        "setup",
        "link",
        "help",
        "build",
        "strategy",
    ]

    NOT_REGISTERED_ALLOWED = ["register", "event"]

    EXCEPTION_CHANNEL = "exceptions"

    def __init__(self, database: DatabaseHandler, server: DiscordServer, loop: asyncio.BaseEventLoop):
        """
        :param database: DatabaseHandler instance
        :param server: The server linked to this bot
        :param loop: The asyncio loop this bot is running in
        """
        with open("participants.txt") as fi:
            self.participants = [line.strip() for line in fi.readlines()]
        self.bot = commands.Bot(self.PREFIX, description=self.DESCRIPTION)
        self.db = database
        self.logger = setup_logger("DiscordBot", "bot.log")
        self.setup_commands()
        self.server = server
        self.overview_messages = dict()
        self.loop = loop
        self.loop.create_task(self.server_status_monitor())
        self.loop.create_task(self.matches_monitor())
        self.ship_cache = dict()
        self.loop.create_task(self.cleanup_cache())
        self.raven = self.open_raven_client()

    async def cleanup_cache(self):
        """
        Clean-up the ship cache

        The ship_cache attribute stores recently accessed Ship objects
        so they do not have to be deserialized continuously. They are
        removed from the cache (and thus memory) after ten minutes.
        """
        for key, (last, _) in self.ship_cache.copy().items():
            if (datetime.now() - last).total_seconds() > 600:
                del self.ship_cache[key]
        await asyncio.sleep(300)
        self.loop.create_task(self.cleanup_cache())

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
        Process a message in the channel the bot has access to

        Only messages starting with the command prefix are processed.
        The amount of arguments is checked, and then the command is
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
            if await self.validate_message(message) is False:
                return
            command, args = await self.process_command(message)
            if command is None:
                await self.invalid_command(channel, author)
                return
            command = DiscordBot.COMMANDS[command]
            mess = command[2] if len(command) == 3 else False
            arguments = (channel, author, args) if not mess else (channel, author, args, message)
            func_name = command[1]
            if "." in func_name:
                exec("from bot.{} import {}".format(*func_name.split(".")))
                func = locals()[func_name.split(".")[1]]
                arguments = (self, *arguments)
            else:
                func = self.__getattribute__(func_name)
            await func(*arguments)
        except Exception as e:
            await self.bot.send_message(
                message.channel, "Sorry, I encountered an error. It has been reported.")
            self.raven.captureException()
            self.exception_handler(
                self.loop, {"exception": e, "message": str(e)})

    def run(self, token: str):
        """Run the Bot loop"""
        try:
            self.bot.run(token)
        except KeyboardInterrupt:
            self.bot.close()

    async def server_status_monitor(self):
        """
        Monitor the server status and send a message upon changes

        This runs as a coroutine, continuously monitoring the status of
        each server and sending a message to all available channels if
        the server status changes.
        """
        statuses = dict()
        messages = list()
        servers = await get_server_status()
        for server, status in servers.items():
            if server not in statuses:
                statuses[server] = "online"
            if status == statuses[server]:
                continue
            messages.append(locals()["SERVER_{}".format(status).upper()].format(server))
        for message in messages:
            for channel in self.validated_channels:
                await self.bot.send_message(channel, message)
        await asyncio.sleep(60)
        self.loop.create_task(self.server_status_monitor())

    async def matches_monitor(self):
        """
        Monitor the matches running on each server

        This runs as a coroutine, continuously monitoring the running
        matches on each server by receiving data from
        """
        try:
            message = build_matches_overview_string(self.server.matches.copy())
            message = MATCHES_TABLE.format(message, datetime.now().strftime("%H:%m:%S"))
            for channel in self.overview_channels:
                if channel in self.overview_messages:
                    try:
                        await self.bot.edit_message(self.overview_messages[channel], message)
                    except RuntimeError:
                        await self.bot.login()
                    continue
                async for message in self.bot.logs_from(channel, limit=1):
                    if message.author.display_name == "GSF Parser":
                        self.overview_messages[channel] = message
                self.overview_messages[channel] = await self.bot.send_message(channel, message)
        except Exception:
            self.raven.captureException()
        await asyncio.sleep(30)
        self.loop.create_task(self.matches_monitor())

    @property
    def validated_channels(self) -> list:
        """Generator for all valid channels this Bot is in"""
        channels = list()
        for server in self.bot.servers:
            for channel in server.channels:
                if self.validate_channel(channel) is False:
                    continue
                channels.append(channel)
        return channels

    @property
    def overview_channels(self) -> list:
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

    async def random_ship(self, channel: Channel, user: DiscordUser, args: tuple):
        """
        Send a random ship tier string to the requesting user

        The ship sent is chosen completely at random. The user can
        specify a specific ship type by using a single argument.
        """
        if len(args) == 0:
            args = (None,)
        category, = args
        ship = await get_random_ship(category)
        if ship is None:
            await self.bot.send_message(channel, INVALID_ARGS)
            return
        message = RANDOM_SHIP.format(ship)
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

    async def get_images(self, message: Message, to_edit: Message = None) -> dict:
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

    async def validate_message(self, message: Message):
        """Check if this message is a valid command for the bot"""
        author, channel, content = message.author, message.channel, message.content
        if not self.validate_channel(channel):
            return False
        if not (isinstance(content, str) and len(content) > 1 and content[0] == DiscordBot.PREFIX):
            return False
        # Validate that the user is registered and has contribute data recently
        tag = generate_tag(author)
        if not self.db.get_user_in_database(tag) and "register" not in content:
            await self.bot.send_message(channel, NOT_REGISTERED)
            self.logger.debug("{} not in database.".format(tag))
            return False
        for command in self.NOT_REGISTERED_ALLOWED:
            if command in content:
                return True
        # if self.db.get_user_in_database(tag) and not self.db.get_user_accessed_valid(tag):
        #     await self.bot.send_message(channel, INACTIVE)
        #     return False
        return True

    @staticmethod
    def validate_channel(channel: Channel):
        """Check if this message was sent in a valid channel for the Bot"""
        return not (channel.name not in DiscordBot.CHANNELS and DiscordBot.CHANNELS_ENFORCED and not channel.is_private)

    async def process_command(self, message: Message):
        """Split the message into command and arguments"""
        content, channel = message.content, message.channel
        command, arguments = await DiscordBot.parse_command(content)
        if command is None:
            return
        if command is False:
            await self.bot.send_message(channel, UNKNOWN_DATE_FORMAT)
            return
        if command not in DiscordBot.COMMANDS or len(arguments) not in DiscordBot.COMMANDS[command][0]:
            return None, None
        return command, tuple(arguments)

    @staticmethod
    async def parse_command(message: str) -> tuple:
        """
        Parse a given command message for the command and the arguments

        A command is given with arguments. The arguments should be
        separated by spaces, or enclosed in quotes if they belong
        together as a single argument. Also attempts to parse the
        arguments as dates where possible, and form datetime instances
        from them with the dateparser package.
        """
        elements = message.split(" ")
        # The first element should be the command
        command, arguments = elements[0], elements[1:]
        if not command.startswith(DiscordBot.PREFIX):  # Not a command
            return None, None
        command = command.replace(DiscordBot.PREFIX, str())
        # The command is valid, so now the arguments for it must be parsed
        hold, args = str(), list()
        for element in arguments:
            # If the element starts with a quote, then it should be held
            if element.startswith("\""):
                element = element.replace("\"", str())
                hold += element + " "
                continue
            # If an argument is on hold, the quotes are not closed
            if len(hold) != 0:
                # If the element ends with a quote, then append the argument
                if element.endswith("\""):
                    element = element.replace("\"", str())
                    hold += element
                    args.append(hold)
                    hold = str()
                    continue
                # The element is one in between quotes
                hold += element + " "
                continue
            # The argument is a normal argument
            args.append(element)
        # Parse arguments required as dates or datetimes
        if command in DiscordBot.DATES:
            dates = DiscordBot.DATES[command]
            for i, (arg, date) in enumerate(zip(args, dates)):
                if date is True:
                    try:
                        args[i] = parse_date(arg)
                    except ValueError:
                        return False, False
        return command, args

    async def event(self, channel: Channel, user: DiscordUser, args: tuple, message: Message):
        """Random ship event bot command"""
        command = args[0]
        if command == "participate":
            name = user.name
            if len(args) == 2:
                name = args[1]
            if name in self.participants:
                await self.bot.send_message(channel, "You are already registered as a participant.")
                return
            self.participants.append(name)
        elif command == "quit":
            if user.name not in self.participants:
                await self.bot.send_message(channel, "You are not participating.")
                return
            self.participants.remove(user.name)
        elif command == "roll":
            for name in self.participants:
                if name.strip() == "":
                    continue
                user = None
                for member in message.server.members:
                    if name == member.name:
                        user = member
                mention = user.mention if user is not None else name
                ship = await get_random_ship()
                await self.bot.send_message(
                    channel, "{}, you are playing {}.".format(mention, ship))
        elif command == "dissolve":
            self.participants.clear()
            await self.bot.send_message(channel, "The participant list has been cleared.")
        else:
            await self.bot.send_message(channel, "I don't understand your meaning.")
            return
        with open("participants.txt", "w") as fo:
            for name in self.participants:
                fo.write("{}\n".format(name))
            fo.write("\n")

    async def strategy(self, channel: Channel, user: DiscordUser, args: tuple):
        """
        Strategy manager for the Discord bot

        Commands:
        - list (default): List all the strategies owned by the user
        - show {strategy}: Show the details of a specific strategy
        - render {strategy}: Render a strategy's phases to PNG and show
        - delete {strategy}: Delete a given strategy by name
        """
        if len(args) == 0:
            args = ("list",)
        command = args[0]
        if command != "list" and len(args) == 1:
            await self.bot.send_message(channel, INVALID_ARGS)
            return
        tag = generate_tag(user)

        if command == "list":
            strategies = self.db.get_strategies(tag)
            if strategies is None or len(strategies) == 0:
                await self.bot.send_message(channel, "You have uploaded no strategies.")
                return
            message = "Strategies registered for {}:\n```markdown\n{}\n```".format(
                user.mention, "\n".join(list("- {}".format(a) for a in strategies)))
            await self.bot.send_message(channel, message)
            return

        name = args[1]
        strategy = self.db.get_strategy_data(tag, name)
        if strategy is None:
            await self.bot.send_message(channel, UNKNOWN_STRATEGY)
            return
        strategy = Strategy.deserialize(strategy)

        if command == "delete":
            self.db.delete_strategy(tag, name)
            await self.bot.send_message(channel, STRATEGY_DELETE.format(name))

        elif command == "show":
            map_type, map_name = strategy.map
            embed = await self.build_embed(
                "{}: {}".format(tag.split("#")[0][1:], strategy.name),
                strategy.description,
                [("Phases", "\n".join("- {}".format(a) for a in strategy.phases)),
                 ("Map", map_names[map_type][map_name])]
            )
            await self.bot.send_message(channel, embed=embed)

        elif command == "render":
            if len(args) != 3:
                await self.bot.send_message(channel, INVALID_ARGS)
                return
            phase_name = args[2]
            if phase_name not in strategy.phases:
                await self.bot.send_message(
                    channel, INVALID_PHASE_NAME.format(name, phase_name))
                return
            phase = strategy[phase_name]
            image = render_phase(phase)
            name = tag.split("#")[0][1:]
            title = "{} - {}: {}".format(name, strategy.name, phase.name)
            embed = await self.build_embed(title, phase.description, None, image=image)
            try:
                await self.bot.send_message(channel, embed=embed)
            except discord.errors.Forbidden:
                await self.bot.send_message(channel, EMBED_PERMISSION_ERROR)
        else:
            await self.bot.send_message(channel, INVALID_ARGS)

    async def build_embed(
            self, title: str, description: str,
            fields: (List[Tuple[str]], None), footer: str=None,
            image: Image.Image=None, colour: int=0x3AAA35)->Embed:
        """Build a Discord Embed from the given parameters"""
        if len(description) > 2048:
            description = description[:2040] + "..."
        embed = Embed(title="**{}**".format(title), description=description, colour=colour)
        if footer is None:
            footer = "Copyright (c) 2018 RedFantom, CC BY-NC-SA 4.0"
        embed.set_footer(text=footer)
        if image is not None:
            embed.set_image(url=await self.upload_image(image, title))
        if fields is not None:
            for name, content in fields:
                embed.add_field(name=name, value=content)
        return embed

    async def upload_image(self, image: Image.Image, title: str)->str:
        """Upload an image to the GSF Parser server for use in embeds"""
        title = title.replace(" ", "_").replace(":", "_")
        path = "/var/www/discord.gsfparser.tk/images/{}.png".format(title)
        image.save(path)
        return "http://discord.gsfparser.tk/images/{}.png".format(title)

    def exception_handler(self, loop: asyncio.AbstractEventLoop, context: dict):
        """Handle all exceptions raised in the asyncio tasks"""
        self.raven.captureException()
        exc = context["exception"] if "exceptexception" in context else Exception
        description = "**Message**: {}\n".format(context["message"]) + \
                      "**Traceback**:\n```python\n{}\n```".format(traceback.format_exc())
        embed = Embed(title=str(exc), colour=0xFF0000, description=description)
        embed.set_footer(text="Exception report by GSF Parser Discord Bot. Copyright (c) 2018 RedFantom")
        channel = self.get_channel_by_name(self.EXCEPTION_CHANNEL)
        loop.create_task(self.bot.send_message(channel, embed=embed))

    def get_channel_by_name(self, name: str)->(Channel, None):
        """Search for a channel by name in available channels"""
        for channel in self.validated_channels:
            if channel.name == name:
                return channel
        return None

    @staticmethod
    def open_raven_client():
        with open("sentry") as fi:
            link = fi.read().strip()
        client = RavenClient(link)
        return client
