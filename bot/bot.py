"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
import traceback
# Packages
from dateparser import parse as parse_date
from discord.ext import commands
from discord import User as DiscordUser, Channel, Message, Embed
# Project Modules
from bot.func import *
from bot.strings import *
from bot.messages import *
from bot.static import *
from bot.man import MANUAL
from data.servers import SERVER_NAMES
from database import DatabaseHandler
from parsing import scoreboards as sb
from parsing.renderer import render_phase
from parsing.ships import Ship
from parsing.strategies import Strategy
from server.discord import DiscordServer
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
        "random": ((0, 1), "random_ship"),
        "strategy": ((0, 1, 2, 3), "strategy"),
        # Data Processing
        "scoreboard": ((0, 1), "parse_scoreboard", True),
        "build": (range(2, 20), "build_calculator"),

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

    BUILD_COMMANDS = {
        "create": ((2, 3), "build_create"),
        "select": ((2,), "build_select"),
        "show": ((1,), "build_show"),
        "stats": ((1,), "build_stats"),
        "search": (range(1, 15), "build_search"),
        "delete": ((1,), "build_delete"),
        "lookup": ((1,), "build_lookup"),
    }

    NOT_REGISTERED_ALLOWED = ["register", "event"]

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
            func = self.__getattribute__(command[1])
            mess = command[2] if len(command) == 3 else False
            arguments = (channel, author, args) if not mess else (channel, author, args, message)
            await func(*arguments)
        except Exception:
            await self.bot.send_message(message.channel, "That hurt! ```python\n{}```".format(traceback.format_exc()))

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
            self.logger.error("An error occurred while building the overview message:\n{}".
                              format(traceback.format_exc()))
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

    async def print_manual(self, channel: Channel, author: DiscordUser, args: tuple):
        """Send the DiscordBot manual to a channel"""
        if len(args) == 0:
            args = ("commands",)
        command, = args
        message = MANUAL[command]
        if not channel.is_private:
            message += "Hint: You can use PM to use this command."
        await self.bot.send_message(channel, message)

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

    async def register_user(self, channel: Channel, user: DiscordUser, args: tuple):
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
        self.db.delete_user(tag)
        self.logger.info("Unregistered {}.".format(tag))
        await self.bot.send_message(channel, UNREGISTER_PUBLIC)
        await self.bot.send_message(user, UNREGISTER)

    async def forgot_code(self, channel: Channel, user: DiscordUser, args: tuple):
        """Generate a new access code for the user"""
        tag = generate_tag(user)
        self.logger.info("Generating new access code for {}.".format(tag))
        code = generate_code()
        self.db.update_auth_code(tag, code)
        await self.bot.send_message(user, NEW_CODE.format(code))

    async def day_overview(self, channel: Channel, user: DiscordUser, args: tuple):
        """Send an overview for a specific day"""
        day, = args if len(args) != 0 else datetime.now(),
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

    async def build_calculator(self, channel: Channel, user: DiscordUser, args: tuple):
        """
        Build calculator controllable with the Discord Bot commands

        Valid build calculator commands:
        - create base name public
        - select identifier/category/component/upgrades
        - stats identifier
        - show identifier
        - search {name:} {owner:} {public:} {pw:} {pw2:}
        """
        command, args = args[0], args[1:]
        if command in DiscordBot.BUILD_COMMANDS:
            n_args, func = DiscordBot.BUILD_COMMANDS[command]
            if len(args) in n_args:
                try:
                    await self.__getattribute__(func)(channel, user, args)
                except Exception as e:
                    self.logger.debug(traceback.format_exc())
                    await self.bot.send_message(channel, e)
                return
        await self.bot.send_message(channel, INVALID_ARGS)

    async def build_create(self, channel: Channel, user: DiscordUser, args: tuple):
        """
        Create a new build in the database for the user

        Command Arguments:
            base: r2s, i2s, etc. as ship identifier
            name: name of the build
            public, optional: If the public flag is set, then the build
                is created publicly. If the channel is not private, then
                the build is set to be public by default.
        """
        base, name = args[0], args[1]
        public = len(args) == 3 and args[2] == "public"
        owner = generate_tag(user)
        ship = Ship.from_base(base)
        data = ship.serialize()
        number = self.db.insert_build(owner, name, data, public)
        if number is None:
            raise ValueError("You already have a build with that name")
        self.ship_cache[number] = (datetime.now(), ship)
        await self.bot.send_message(channel, BUILD_CREATE.format(name, ship.name, number))

    async def build_select(self, channel: Channel, user: DiscordUser, args: tuple):
        """
        Select a specific component or crew member for a given ship

        Also checks ownership of the build. The build can only be
        altered by its owner.
        """
        build, element = args
        tag = generate_tag(user)
        build = self.db.get_build_id(build, tag)
        if not self.db.get_build_owner(build) == tag:
            raise PermissionError("Shame on you. That build is not yours.")
        if build in self.ship_cache:
            _, ship = self.ship_cache[build]
        else:
            data = self.db.get_build_data(build)
            ship = Ship.deserialize(data)
        self.ship_cache[build] = (datetime.now(), ship)
        if not isinstance(ship, Ship):
            raise TypeError("Something went horribly wrong, sorry.")
        result = ship.update_element(element, None)
        data = ship.serialize()
        self.db.update_build_data(build, data)
        await self.bot.send_message(channel, result)

    async def build_stats(self, channel: Channel, user: DiscordUser, args: tuple):
        pass

    async def build_show(self, channel: Channel, user: DiscordUser, args: tuple):
        """Show a build upon user request"""
        build, = args
        if not self.db.build_read_access(build, generate_tag(user)):
            raise PermissionError("You do not have access to that build.")
        if build in self.ship_cache:
            _, ship = self.ship_cache[build]
        else:
            data = self.db.get_build_data(build)
            ship = Ship.deserialize(data)
        self.ship_cache[build] = (datetime.now(), ship)
        name = self.db.get_build_name_id(build)
        message = await build_string_from_ship(ship, name)
        await self.bot.send_message(channel, message)

    async def build_search(self, channel: Channel, user: DiscordUser, args: tuple):
        pass

    async def build_delete(self, channel: Channel, user: DiscordUser, args: tuple):
        """Delete a specific build owner by the user either by name or ID"""
        build, = args
        name = self.db.delete_build(build, generate_tag(user))
        await self.bot.send_message(channel, BUILD_DELETE.format(name))

    async def build_lookup(self, channel: Channel, user: DiscordUser, args: tuple):
        path, = args
        if path.startswith("crew"):
            elems = path.split("/")
            if len(elems) != 2:
                raise ValueError("Invalid crew member path: `{}`. Use `crew/part_of_name`".format(path))
            name = elems[1]
            crew_dict = await lookup_crew(name)
            message = await build_string_from_crew_dict(crew_dict)
            await self.bot.send_message(channel, message)
            return
        raise NotImplementedError("This feature has not yet been implemented.")

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
        tag = generate_tag(user)

        if command == "list":
            strategies = self.db.get_strategies(tag)
            if strategies is None or len(strategies) == 0:
                await self.bot.send_message(channel, "You have uploaded no strategies.")
                return
            message = "Strategies registered for {}:\n```markdown\n{}\n```".format(
                user.mention, "\n".join(list("- {}".format(a[0]) for a in strategies)))
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
            message = build_string_from_strategy(tag, strategy)
            await self.bot.send_message(channel, message)

        elif command == "render":
            if len(args) != 3:
                await self.bot.send_message(channel, INVALID_ARGS)
                return
            phase_name = args[2]
            if phase_name not in strategy.phases:
                await self.bot.send_message(
                    channel, INVALID_PHASE_NAME.format(name, phase_name))
                return
            image = render_phase(strategy[phase_name])
            file_name = get_temp_file(".png", user)
            image.save(file_name)
            message = await self.bot.send_file(channel, image)
            link = message.attachments[0]["url"]
            await self.bot.delete_message(message)
            embed = Embed()
            embed.set_footer(text="Generated by GSF Parser Discord Bot. Copyright (C) 2018 RedFantom")
            embed.description = strategy.description
            embed.title = "{} - {}".format(strategy.name, phase_name)
            embed._colour = 3844661
            embed.set_image(url=link)
            self.bot.send_message(channel, embed=embed)

        else:
            await self.bot.send_message(channel, INVALID_ARGS)
