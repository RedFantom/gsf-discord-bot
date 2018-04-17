"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
import requests
import asyncio
import discord
from discord.ext import commands


command_prefix = "$"
description = "GSF Parser-based Discord Bot"
bot = commands.Bot(command_prefix, description=description)


@bot.event
async def on_ready():
    print("Logged in as: {}, {}".format(bot.user.name, bot.user.id))


if __name__ == '__main__':
    bot.run()
