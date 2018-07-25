"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import Channel, User as DiscordUser
# Project Modules
from bot.embeds import *
from bot.messages import *
from parsing.ships import Ship, lookup_crew, lookup_component
from parsing.shipstats import ShipStats
from utils import generate_tag

BUILD_COMMANDS = {
    "create": (2, 3),
    "select": (2,),
    "show": (1,),
    "stats": (1,),
    "search": tuple(range(1, 15)),
    "delete": (1,),
    "lookup": (1,),
    "list": (0,),
}

_list = list


async def create(self, channel: Channel, user: DiscordUser, args: tuple):
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
        await self.bot.send_message(channel, "You already have a build with that name.")
        return
    await self.bot.send_message(channel, BUILD_CREATE.format(name, ship.name, number))


async def select(self, channel: Channel, user: DiscordUser, args: tuple):
    """
    Select a specific component or crew member for a given ship

    Also checks ownership of the build. The build can only be
    altered by its owner.
    """
    build, element = args
    tag = generate_tag(user)
    build = self.db.get_build_id(build, tag)
    if not self.db.get_build_owner(build) == tag:
        await self.bot.send_message(channel, "Shame on you. That build is not yours.")
        return
    data = self.db.get_build_data(build)
    ship = Ship.deserialize(data)
    result = ship.update_element(element, None)
    data = ship.serialize()
    self.db.update_build_data(build, data)
    await self.bot.send_message(channel, result)


async def stats(self, channel: Channel, user: DiscordUser, args: tuple):
    """Show the statistics of a specific build"""
    build, = args
    if not self.db.build_read_access(build, generate_tag(user)):
        await self.bot.send_message(channel, "You do not have access to that build.")
        return
    if not channel.is_private:
        await self.bot.send_message(channel, "I only want to do this in PM due to the large statistics list.")
    data = self.db.get_build_data(build)
    name = self.db.get_build_name_id(build)
    ship = Ship.deserialize(data)
    stats = ShipStats(ship, None, None)
    embed = embed_from_stats(stats, name)
    await self.bot.send_message(channel, embed=embed)


async def show(self, channel: Channel, user: DiscordUser, args: tuple):
    """Show a build upon user request"""
    build, = args
    if not self.db.build_read_access(build, generate_tag(user)):
        await self.bot.send_message(channel, "You do not have access to that build.")
        return
    data = self.db.get_build_data(build)
    ship = Ship.deserialize(data)
    name = self.db.get_build_name_id(build)
    embed = embed_from_ship(ship, name)
    await self.bot.send_message(channel, embed=embed)


async def search(self, channel: Channel, user: DiscordUser, args: tuple):
    pass


async def delete(self, channel: Channel, user: DiscordUser, args: tuple):
    """Delete a specific build owner by the user either by name or ID"""
    build, = args
    name = self.db.delete_build(build, generate_tag(user))
    await self.bot.send_message(channel, BUILD_DELETE.format(name))


async def lookup(self, channel: Channel, user: DiscordUser, args: tuple):
    path, = args
    elems = path.split("/")
    if len(elems) != 2:
        await self.bot.send_message(channel, "The lookup command requires a two element path.")
        return
    if path.startswith("crew"):
        name = elems[1]
        crew_dict = lookup_crew(name)
        if crew_dict is None:
            await self.bot.send_message(channel, INVALID_COMPONENT_PATH)
            return
        embed = embed_from_crew_dict(crew_dict)
        await self.bot.send_message(channel, embed=embed)
    else:
        category, name = elems
        component = lookup_component(category, name)
        if component is None:
            await self.bot.send_message(channel, INVALID_COMPONENT_PATH)
            return
        embed = embed_from_component(component)
        await self.bot.send_message(channel, embed=embed)


async def list(self, channel: Channel, user: DiscordUser, args: tuple):
    """List all the builds owned by a certain user"""
    tag = generate_tag(user)
    builds = _list(self.db.get_builds_owner(tag))
    if len(builds) == 0:
        await self.bot.send_message(channel, "You have not created any builds.")
        return
    embed = embed_from_builds(builds, tag, channel.is_private)
    await self.bot.send_message(channel, embed=embed)


async def calculator(self, channel: Channel, user: DiscordUser, args: tuple):
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
    if command in BUILD_COMMANDS:
        n_args = BUILD_COMMANDS[command]
        if len(args) in n_args:
            try:
                await globals()[command](self, channel, user, args)
            except Exception as e:
                await self.bot.send_message(channel, "An error occurred while processing your command.")
                self.raven.captureException()
                self.exception_handler(self.loop, {"exception": e, "message": str(e)})
            return
    await self.bot.send_message(channel, INVALID_ARGS)
