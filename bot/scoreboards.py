"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import TextChannel as Channel, User as DiscordUser, Message
# Project Modules
from parsing import scoreboards as sb
from utils.utils import get_temp_file


SCOREBOARD_UI_SCALE = "Results are more reliable if you use a Global UI Scale of `1.0` or more."
INVALID_ARGS = "Invalid result type argument `{}`. Choose `table` (default), `excel` or `csv`."
NOT_A_SCOREBOARD = "I do not recognize that image as a screenshot of a scoreboard.\n\n" \
                   "If it is a scoreboard, please send this message to the Maker " \
                   "to ask if support for this size and scale can be implemented. " \
                   "You must include this image, as well as your Global UI Scaling Factor."


async def parse(self, channel: Channel, user: DiscordUser, args: tuple, message: Message):
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
        await self.send_message(channel, INVALID_ARGS.format(type))
        return
    await self.send_message(channel, "I'm evaluating your screenshot now.")
    images = await self.get_images(message)
    for name, image in images.items():
        scale, location = sb.is_scoreboard(image)
        if scale is None or location is None:
            await self.send_message(channel, NOT_A_SCOREBOARD)
            return
        if scale < 1.0:
            await self.send_message(channel, SCOREBOARD_UI_SCALE)
        to_edit = await channel.send("All right, that's a scoreboard. I'm working on it...")
        results = await sb.parse_scoreboard(image, scale, location, self.bot, to_edit)
        if "table" in args:
            message = "```diff\n{}```".format(sb.format_results(results))
            await self.send_message(channel, message)
        else:
            df = sb.results_to_dataframe(results)
            await send_dataframe(self, type, df, channel, user)


async def send_dataframe(self, type: str, df, channel: Channel, user: DiscordUser):
    """Send a Pandas DataFrame instance as a file to a channel"""
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
