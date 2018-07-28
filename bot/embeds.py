"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from collections import OrderedDict
# Packages
from discord import Embed
from github import GitRelease
# Project Modules
from bot.static import EMBED_FOOTER
from bot.strings import build_mine_string, get_value_string
from data.components import \
    COMPONENT_KEYS
from data import statistics as stats
from parsing.ships import Ship, Component
from parsing.shipstats import ShipStats
from parsing.shipops import TimeToKill
from utils.utils import setup_logger

logger = setup_logger("Embeds", "embeds.log")

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


def embed_from_ship(ship: Ship, name) -> Embed:
    """Build an embed from a Ship with component and crew details"""
    title = "__{}__ ({})".format(name, ship.name)
    comps_field = str()
    for key in COMPONENT_KEYS:
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


def embed_from_stats(shipstats: ShipStats, name: str) -> Embed:
    """Build a rich embed from a ShipStats instance"""
    fields = OrderedDict()
    stats_ship = shipstats["Ship"].copy()
    for stat, val in stats_ship.items():
        stats_ship[stat] = get_value_string(stat, val)
    fields["Hull and Shields"] = stats.HULL_AND_SHIELDS_STATS_STRING.format(**stats_ship)
    fields["Engine"] = stats.ENGINE_STATS_STRING.format(**stats_ship)
    fields["Weapons"] = stats.WEAPON_STATS_STRING.format(**stats_ship)
    fields["Sensors"] = stats.SENSOR_STATS_STRING.format(**stats_ship)
    for weapon in ShipStats.PRIMARY_WEAPON:
        if weapon not in shipstats:
            continue
        weapon_stats = shipstats[weapon].copy()
        for stat, val in weapon_stats.items():
            weapon_stats[stat] = get_value_string(stat, val)
        field_name = "{}: {}".format(weapon, shipstats.ship[weapon].name).replace("2", "")
        fields[field_name] = stats.PRIMARY_WEAPON_STATS_STRING.format(**weapon_stats)
    for weapon in ShipStats.SECONDARY_WEAPON + ("Systems",):
        if weapon not in shipstats:
            continue
        weapon_stats = dict()
        for stat, val in shipstats[weapon].items():
            weapon_stats[stat] = get_value_string(stat, val)
        field_name = "{}: {}".format(weapon, shipstats.ship[weapon].name).replace("2", "")
        weapon_name = shipstats.ship[weapon].name
        if "Rocket Pod" in weapon_name:
            fields[field_name] = stats.PRIMARY_WEAPON_STATS_STRING.format(**weapon_stats) + \
                                 stats.AMMO_STRING.format(**weapon_stats)
        elif "Mine" in weapon_name:
            fields[field_name] = build_mine_string(shipstats[weapon])
        elif "Railgun" in weapon_name:
            fields[field_name] = stats.RAILGUN_STATS_STRING.format(**weapon_stats)
        elif "Missile" in weapon_name:
            fields[field_name] = stats.MISSILE_STATS_STRING.format(**weapon_stats)
        else:
            logger.debug("{}".format(weapon_name))
    title = "{}: Statistics".format(name)
    embed = Embed(title=title, colour=0x4286f4)
    for name, value in fields.items():
        embed.add_field(name="__**{}**__".format(name.replace("_", " ")), value=value, inline=False)
    return embed


def embed_from_ttk(ttk: TimeToKill, source_name: str, target_name: str, source: Ship, target: Ship, acc: bool) -> Embed:
    """Build an embed from a TTK calculation result"""
    title = "Time To Kill Calculation"
    description = \
        "**Source**: {} ({})\n".format(source_name, source.name) + \
        "**Target**: {} ({})\n".format(target_name, target.name) + \
        "**Distance**: {}m\n".format(ttk.distance * 100) + \
        "**Weapon**: `{}`\n".format(ttk.weapon) + \
        "Accuracy/Evasion **was{}** accounted for.\n".format("" if acc is True else " not") + \
        "**Effective target health**: {:.0f}, {:.0f}\n".format(ttk.args[-1], ttk.args[-2])
    embed = Embed(title=title, description=description, colour=0xff2600)
    embed.add_field(
        name="Results",
        value="*Shots Required*: {}\n".format(ttk.shots) +
              "*Time Required*: {:.1f}s\n".format(ttk.time))
    if not all(len(actives) == 0 for actives in ttk.actives.values()):
        value = "".join("*{}*: {}\n".format(key.capitalize(), ", ".join(active_list))
                        for key, active_list in ttk.actives.items()
                        if len(active_list) != 0)
        if value != "":
            embed.add_field(name="Active Abilities", value=value, inline=False)
    embed.set_footer(text=EMBED_FOOTER)
    return embed
