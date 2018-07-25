"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import Embed


component_colors = {
    "PrimaryWeapon": 0xffa500,
    "PrimaryWeapon2": 0xffa500,
    "SecondaryWeapon": 0xff3b00,
    "SecondaryWeapon2": 0xff3b00,
    "Systems": 0x003d60,
    "ShieldProjector": 0x00c472,
    "Engine": 0x793ab7,
    "Armor": 0x600000,
    "Reactor": 0x4abc40,
    "Magazine": 0xccc92e,
    "Thruster": 0xb20038,
    "Sensor": 0x011849,
    "Capacitor": 0xaf0000,
}


def truncate(text, length=2048):
    """Truncate a string to a specific length"""
    if len(text) < length:
        return text
    text = text[:length - 3 - 1] + "..."
    return text


def embed_from_crew_dict(member: dict) -> Embed:
    """Build embed fields from crew dict"""
    title = member["Category"] + ": " + member["Name"]
    description = truncate(member["Description"])
    fields = list()
    for key in ["Ability", "Passive", "SecondaryPassive"]:
        fields.append((member["{}Name".format(key)], member["{}Description".format(key)]))
    colour = 0xb90505 if member["Faction"] == "Imperial" else 0x085195
    embed = Embed(title=title, description=description, colour=colour)
    for header, (name, value) in zip(("Ability", "Passive", "Passive"), fields):
        embed.add_field(name="{}: {}".format(header, name), value=value, inline=False)
    return embed


def embed_from_component(component: dict) -> Embed:
    """Build embed with fields from component dict"""
    title = "{}: {}".format(component["Category"], component["Name"])
    description = truncate(component["Description"])
    colour = component_colors[component["Category"]]
    embed = Embed(title=title, description=description, colour=colour)
    for choice in component["TalentTree"]:
        for talent in choice:
            embed.add_field(name=talent["Name"], value=talent["Description"], inline=len(choice) == 2)
    return embed
