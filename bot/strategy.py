"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Pacakages
from discord import Channel, User as DiscordUser
import discord.errors
# Project Modules
from bot.embeds import embed_from_phase_render
from bot.messages import \
    INVALID_ARGS, EMBED_PERMISSION_ERROR, UNKNOWN_STRATEGY, \
    STRATEGY_DELETE, INVALID_PHASE_NAME
from data.maps import map_names
from parsing.strategies import Strategy
from parsing.renderer import render_phase
from utils import generate_tag


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
             ("Map", map_names[map_type][map_name])])
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
        url = await self.upload_image(image)
        embed = embed_from_phase_render(tag, url, strategy, phase)
        try:
            await self.bot.send_message(channel, embed=embed)
        except discord.errors.Forbidden:
            await self.bot.send_message(channel, EMBED_PERMISSION_ERROR)
    else:
        await self.bot.send_message(channel, INVALID_ARGS)
