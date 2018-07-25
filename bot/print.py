"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import Channel, User as DiscordUser
# Project Modules
from .man import MANUAL
from .static import *
from .messages import *
from .func import get_download_link, get_server_status


async def print_manual(self, channel: Channel, author: DiscordUser, args: tuple):
    """Send the DiscordBot manual to a channel"""
    if len(args) == 0:
        args = ("commands",)
    command, = args
    if command not in MANUAL:
        await self.bot.send_message(channel, "That is not a command in my manual.")
        return
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
    """Print the author information message as an embed"""
    embed = await self.build_embed(*AUTHOR_EMBED, fields=[CONTENT_LICENSE, CODE_LICENSE], colour=0x0000FF)
    await self.bot.send_message(channel, embed=embed)


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