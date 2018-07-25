"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import Embed
# Project Modules
from utils.utils import setup_logger


logger = setup_logger("Embeds", "embeds.log")


def embed_from_crew_dict(member: dict) -> Embed:
    """Build embed fields from crew dict"""
    title = member["Category"] + ": " + member["Name"]
    description = member["Description"]
    if len(description) > 2048:
        description = description[:2000] + "..."
    fields = list()
    for key in ["Ability", "Passive", "SecondaryPassive"]:
        fields.append((member["{}Name".format(key)], member["{}Description".format(key)]))
    image = "http://discord.gsfparser.tk/icons/{}.jpg".format(member["Icon"].lower())
    logger.debug("Crew Icon: {}".format(image))
    colour = 0xb90505 if member["Faction"] == "Imperial" else 0x085195
    embed = Embed(title=title, description=description, colour=colour)
    embed.set_image(url=image)
    for header, (name, value) in zip(("Ability", "Passive", "Passive"), fields):
        embed.add_field(name="{}: {}".format(header, name), value=value, inline=False)
    return embed