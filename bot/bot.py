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
from discord.ext import commands
from discord import \
    User as DiscordUser, Channel, Message, Embed, Server, PrivateChannel
from raven import Client as RavenClient
# Project Modules
from bot.embeds import embed_from_ship
from bot.func import *
from bot.strings import *
from bot.messages import *
from data.servers import SERVER_NAMES
from database import DatabaseHandler
from parsing.ships import Ship
from server.discord import DiscordServer
from settings import settings
from utils import setup_logger, generate_tag
from utils.utils import DATE_FORMAT, TIME_FORMAT


class DiscordBot(object):
    """
    Run a Discord bot for GSF Parser users. For a list commands, check
    the man.py file.
    """

    DESCRIPTION = "A friendly bot to socially interact with GSF " \
                  "statistics and for research"

    IMAGE_TYPES = ("png", "jpg", "bmp")

    COMMANDS = {
        # Help commands
        "man": ((0, 1), "print.manual"),
        "servers": ((0,), "print.servers"),
        "bot_author": ((0,), "print.author"),
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
        "strategy": ((0, 1, 2, 3), "strategy.strategy"),
        # Data Processing
        "scoreboard": ((0, 1), "scoreboards.parse", True),
        "build": (range(1, 20), "build.calculator"),
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

    NOT_REGISTERED_ALLOWED = ["register", "event", "help", "setup", "link"]

    EXCEPTION_CHANNEL = settings["exceptions"]["channel"]

    def __init__(self, database: DatabaseHandler, server: DiscordServer, loop: asyncio.BaseEventLoop):
        """
        :param database: DatabaseHandler instance
        :param server: The server linked to this bot
        :param loop: The asyncio loop this bot is running in
        """
        with open("participants.txt") as fi:
            self.participants = [line.strip() for line in fi.readlines()]
        self.bot = commands.Bot(settings["bot"]["prefix"], description=self.DESCRIPTION)
        self.db = database
        self.logger = setup_logger("DiscordBot", "bot.log")
        self.setup_commands()
        self.server = server
        self.overview_messages = dict()
        self.loop = loop
        # self.loop.create_task(github_monitor(self))
        # self.loop.create_task(self.server_status_monitor())
        # self.loop.create_task(self.matches_monitor())
        self.raven = None

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
            if await self.validate_message(message) is False:
                return
            message, channel = await self.process_redirect(message)
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
        if settings["matches"]["monitor"] is False:
            return
        try:
            message = build_matches_overview_string(self.server.matches.copy())
            message = MATCHES_TABLE.format(message, datetime.now().strftime("%H:%m:%S"))
            for channel in self.get_channels_by_name(settings["matches"]["channel"]):
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
                if channel.name in settings["bot"]["channels"]:
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
        if await self.validate_author(message) is False:
            self.logger.debug("Author failed validation: {}".format(message.author.display_name))
            return False
        if await self.validate_content(message) is False:
            self.logger.debug("Content failed validation: {}".format(message.content))
            return False
        if await self.validate_channel(message) is False:
            self.logger.debug("Channel failed validation: {}".format(message.channel.name))
            return False
        return True

    async def validate_content(self, message: Message):
        """Validate the content of a message"""
        author, channel, content = message.author, message.channel, message.content
        if not (isinstance(content, str) and len(content) > 1 and content[0] == settings["bot"]["prefix"]):
            return False
        tag = generate_tag(author)
        if not self.db.get_user_in_database(tag) and "register" not in content:
            await self.bot.send_message(channel, NOT_REGISTERED)
            self.logger.debug("{} not in database.".format(tag))
            return False
        for command in self.NOT_REGISTERED_ALLOWED:
            if command in content:
                return True
        if channel.is_private is True and not any(command in content for command in DiscordBot.PRIVATE):
            await self.bot.send_message(author, NOT_PRIVATE)
            return False
        return True

    async def validate_channel(self, message: Message):
        """Validate the channel the message was sent in as valid"""
        channel = message.channel
        if isinstance(channel, PrivateChannel):
            return True
        return channel in self.validated_channels

    async def validate_author(self, message: Message):
        """Determine whether a user is allowed to use the bot"""
        author, server = message.author, message.server
        if author == self.bot.user:
            return False
        if not isinstance(author, DiscordUser):
            return
        if settings["bot"]["role"] is not None:
            if not isinstance(server, Server):
                return False
            member = server.get_member(author.id)
            if member is None:
                return False
            if settings["bot"]["role"] not in [role.name for role in member.roles]:
                return False
        # if self.db.get_user_in_database(tag) and not self.db.get_user_accessed_valid(tag):
        #     await self.bot.send_message(channel, INACTIVE)
        #     return False
        return True

    async def process_redirect(self, message: Message)->Tuple[Message, Channel]:
        """
        Determine if the message requests a redirect of channel

        The Bot allows redirecting command results to channels that
        would not normally allow bot commands. This can be done with the
        `->` operator, mentioning a single channel after this marker.
        """
        content, channel = message.content, message.channel
        elems = content.split("->")
        if len(elems) == 2:
            content = elems[0].strip()
            message.content = content
            if not channel.is_private:
                channel_name = elems[1].strip()
                assert isinstance(message.server, Server)
                for server_channel in message.server.channels:
                    assert isinstance(server_channel, Channel)
                    if server_channel.mention == channel_name:
                        channel = server_channel
                        break
        return message, channel

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
        if not command.startswith(settings["bot"]["prefix"]):  # Not a command
            return None, None
        command = command.replace(settings["bot"]["prefix"], str())
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
            await self.bot.send_message(channel, "{}, you just joined the event!".format(user.mention))
        elif command == "quit":
            if user.name not in self.participants:
                await self.bot.send_message(channel, "You are not participating.")
                return
            self.participants.remove(user.name)
            await self.bot.send_message(channel, "{}, you are no longer participating.".format(user.mention))
        elif command == "roll":
            for name in self.participants:
                if name.strip() == "":
                    continue
                user = None
                for member in message.server.members:
                    if name == member.name:
                        user = member
                mention = user.mention if user is not None else name
                ship = Ship.random()
                await self.bot.send_message(
                    channel, "{}, you are playing {}.".format(mention, ship.name),
                    embed=embed_from_ship(ship, "Random ({}, {})".format(
                        name, datetime.now().strftime("%H:%M")), False))
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

    async def upload_image(self, image: Image.Image, title: str) -> str:
        """Upload an image to the GSF Parser server for use in embeds"""
        title = title.replace(" ", "_").replace(":", "_")
        path = "/var/www/{}/images/{}.png".format(settings["bot"]["http"], title)
        image.save(path)
        return "{}/images/{}.png".format(settings["bot"]["http"], title)

    def exception_handler(self, loop: asyncio.AbstractEventLoop, context: dict):
        """Handle all exceptions raised in the asyncio tasks"""
        self.logger.error(traceback.format_exc())
        if not settings["exceptions"]["enabled"]:
            return
        if self.raven is None:
            self.raven = RavenClient(settings["exceptions"]["raven"])
        try:
            self.raven.captureException()
            exc = context["exception"] if "exception" in context else Exception
            description = "**Message**: {}\n".format(context["message"]) + \
                          "**Traceback**:\n```python\n{}\n```".format(traceback.format_exc())
            embed = Embed(title=str(exc), colour=0xFF0000, description=description)
            channel = self.get_channel_by_name(settings["exceptions"]["channel"])
            loop.create_task(self.bot.send_message(channel, embed=embed))
        except Exception as e:
            self.raven.captureException(
                extra={"platform": settings["exceptions"]["platform"]})
            self.logger.error(traceback.format_exc())

    def get_channel_by_name(self, name: str) -> (Channel, None):
        """Search for a channel by name in available channels"""
        for channel in self.validated_channels:
            if channel.name == name:
                return channel
        return None

    def get_channels_by_name(self, name: str) -> List[Channel]:
        """Return a list of channels with a given channel name"""
        channels = list()
        for channel in self.validated_channels:
            if channel.name == name:
                channels.append(channel)
        return channels

    async def build_embed(self, title, description, image: Image.Image)->Embed:
        """Build a Discord Embed from the given parameters"""
        if len(description) > 2048:
            description = description[:2040] + "..."
        embed = Embed(title="**{}**".format(title), description=description, colour=3844661)
        embed.set_footer(text="Generated by GSF Parser Discord Bot. Copyright (c) 2018 RedFantom")
        embed.set_image(url=await self.upload_image(image, title))
        return embed
