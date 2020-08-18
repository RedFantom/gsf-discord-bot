"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from datetime import datetime
# Packages
from discord import TextChannel as Channel, User as DiscordUser
# Project Modules
from bot.messages import *
from bot.strings import build_string_from_servers, build_string_from_matches
from data.servers import SERVER_NAMES
from utils.utils import DATE_FORMAT


async def day(self, channel: Channel, user: DiscordUser, args: tuple):
    """Send an overview for a specific day"""
    day, = args if len(args) != 0 else datetime.now(),
    day = day.strftime(DATE_FORMAT)
    servers = {server: 0 for server in SERVER_NAMES.keys()}
    servers.update(self.db.get_matches_count_by_day(day))
    message = build_string_from_servers(servers)
    message = MATCH_COUNT_DAY.format(day, message)
    await self.send_message(channel, message)


async def period(self, channel: Channel, user: DiscordUser, args: tuple):
    """Send the overview like that of a day for a period"""
    if len(args) == 1:
        args += (datetime.now(),)
    start, end = args
    start_s, end_s = map(lambda dt: dt.strftime(DATE_FORMAT), (start, end))
    if end <= start:
        await self.send_message(channel, INVALID_DATE_RANGE)
        return
    servers = self.db.get_matches_count_by_period(start, end)
    message = build_string_from_servers(servers)
    message = MATCH_COUNT_PERIOD.format(start_s, end_s, message)
    await self.send_message(channel, message)


async def week(self, channel: Channel, user: DiscordUser, args: tuple):
    """Send the overview like that of a day for the last week"""
    servers = self.db.get_matches_count_by_week()
    message = build_string_from_servers(servers)
    await self.send_message(channel, MATCH_COUNT_WEEK.format(message))


async def matches(self, channel: Channel, user: DiscordUser, args: tuple):
    """Send an overview of matches for a given server"""
    server = args[0]
    if server not in SERVER_NAMES.keys():
        await self.send_message(channel, INVALID_SERVER)
        return
    if len(args) == 2:
        day = args[1].strftime(DATE_FORMAT)
    else:
        day = datetime.now().strftime(DATE_FORMAT)
    matches = self.db.get_matches_by_day_by_server(server, day)
    if len(matches) == 0:
        await self.send_message(channel, NO_MATCHES_FOUND)
        return
    message = MATCH_OVERVIEW.format(day, SERVER_NAMES[server], build_string_from_matches(matches))
    await self.send_message(channel, message)
