"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import Channel, User as DiscordUser
# Project Modules
from bot.embeds import embed_from_manual
from bot.func import get_server_status
from bot.github import get_download_link
from bot.man import MANUAL
from bot.messages import *
from bot.static import *


async def manual(self, channel: Channel, user: DiscordUser, args: tuple):
    """Send the DiscordBot manual to a channel"""
    if len(args) == 0:
        args = ("commands",)
    command, = args
    if command not in MANUAL:
        await self.bot.send_message(channel, "That is not a command in my manual.")
        return
    message = MANUAL[command]
    if isinstance(message, tuple):
        embed = embed_from_manual(message)
        await self.bot.send_message(channel, embed=embed)
        return
    if not channel.is_private:
        message += "Hint: You can use PM to use this command."
    await self.bot.send_message(channel, message)


async def help(self, channel: Channel, user: DiscordUser, args: tuple):
    """Print the HELP message"""
    await self.bot.send_message(channel, HELP)


async def servers(self, channel: Channel, user: DiscordUser, args: tuple):
    """Send a list of servers to the channel with server statuses"""
    servers = await get_server_status()
    if servers is None:
        await self.bot.send_message(channel, "I could not contact the SWTOR website for information.")
        return
    self.logger.debug("Server statuses: {}".format(servers))
    await self.bot.send_message(channel, SERVER_STATUS.format(**servers))


async def bot_author(self, channel: Channel, user: DiscordUser, args: tuple):
    """Print the author information message as an embed"""
    embed = await self.build_embed(*AUTHOR_EMBED, fields=[CONTENT_LICENSE, CODE_LICENSE], colour=0x0000FF)
    await self.bot.send_message(channel, embed=embed)


async def privacy(self, channel: Channel, user: DiscordUser, args: tuple):
    await self.bot.send_message(channel, PRIVACY)


async def purpose(self, channel: Channel, user: DiscordUser, args: tuple):
    await self.bot.send_message(channel, PURPOSE)


async def setup(self, channel: Channel, user: DiscordUser, args: tuple):
    await self.bot.send_message(channel, SETUP)


async def link(self, channel: Channel, user: DiscordUser, args: tuple):
    links = await get_download_link()
    if links is None:
        await self.bot.send_message(channel, GITHUB_RATE_LIMIT)
        return
    await self.bot.send_message(channel, GITHUB_DOWNLOAD_LINK.format(*links))
