"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Packages
from discord import Embed
from github import GitRelease
# Project Modules
from data.components import component_keys
from data import statistics as stats
from parsing.ships import Ship, Component
from parsing.shipstats import ShipStats


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
    letters = {0: "L", 1: "R"}
    title = "{}: {}".format(component["Category"], component["Name"])
    description = truncate(component["Description"])
    colour = component_colors[component["Category"]]
    embed = Embed(title=title, description=description, colour=colour)
    for i, choice in enumerate(component["TalentTree"]):
        for j, talent in enumerate(choice):
            header = str(i + 1) if len(choice) == 1 else "{}{}".format(i + 1, letters[j])
            title = "__{}__: {}".format(header, talent["Name"])
            embed.add_field(name=title, value=talent["Description"], inline=False)
    return embed


def embed_from_manual(entry: tuple) -> Embed:
    """Build a manual embed"""
    command, arguments, description = entry
    title = "Command Manual: `{}`".format(command)
    embed = Embed(title=title, description=description, colour=0xFFFFFF)
    for name, descr, optional, default in arguments:
        field = "__Argument__: `{}`".format(name)
        if optional is True:
            field = "{} [`{}`]".format(field, default)
        embed.add_field(name=field, value=descr)
    return embed


def embed_from_ship(ship: Ship, name)->Embed:
    """Build an embed from a Ship with component and crew details"""
    title = "__{}__ ({})".format(name, ship.name)
    comps_field = str()
    for key in component_keys:
        component = ship.components[key]
        if component is None or not isinstance(component, Component):
            continue
        upgrades = ship.build_upgrade_string(component.upgrades, component.type)
        string = "{}: *{}* ({})\n".format(
            key.capitalize(), component.name,
            upgrades if upgrades != "" else "No upgrades")
        comps_field += string
    if comps_field == "":
        comps_field = "No components selected."
    crew_field = str()
    for role, member in ship.crew.items():
        if member is None:
            member = (None, None, "Unknown")
        _, _, member = member
        crew_field += "{}: *{}*\n".format(role, member)
    embed = Embed(title=title, colour=0x646464)
    embed.add_field(name="Components", value=comps_field, inline=False)
    embed.add_field(name="Crew", value=crew_field, inline=False)
    return embed


def embed_from_builds(builds: list, owner: str, private: bool) -> Embed:
    """Build a list of builds in embed form"""
    title = "Builds created by {}".format(owner.split("#")[0][1:])
    strings = list()
    omitted = False
    for build, name, data, public in builds:
        if private is False and bool(public) is False:
            omitted = True
            continue
        ship = Ship.deserialize(data)
        strings.append("__{}__: {} ({})".format(build, name, ship.name))
    description = "\n".join(strings)
    embed = Embed(title=title, description=description, colour=0x646464)
    if omitted is True:
        embed.set_footer(text="Private builds have been omitted from results.")
    return embed


def embed_from_release(release: GitRelease) -> Embed:
    """Build a rich embed from a GitRelease"""
    embed = Embed(title=release.title, description=release.body, colour=0x000000)
    embed.set_footer(text="Get it from [here]({})".format(release.url))
    return embed


def embed_from_stats(shipstats: ShipStats) -> Embed:
    """Build a rich embed from a ShipStats instance"""
    pass
