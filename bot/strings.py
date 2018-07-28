"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from datetime import datetime
# Project Modules
from bot.messages import MATCHES_ROW
from data.servers import SERVER_NAMES
from data import statistics as stats
from utils import UNKNOWN_MAP, UNKNOWN_END, MAP_NAMES
from utils.utils import TIME_FORMAT

UPGRADE_STR = {
    "R": "Right",
    "L": "Left"
}


def build_string_from_servers(servers: dict):
    """Return a formatted string from a server: match_count dict"""
    message = str()
    for server, count in servers.items():
        message += "{}: {}\n".format(SERVER_NAMES[server], count)
    return message


def build_string_from_matches(matches: list):
    """Return a formatted string from a matches list"""
    string = str()
    for match in sorted(matches, key=lambda tup: tup[0]):
        start, end, map, score = match
        if end is None:
            end = "Unknown"
        if map is not None:
            match_type, match_map = map.split(",")
        else:
            match_type, match_map = "Unknown", "Unknown"
        if score is not None:
            winner = "Empire" if score > 1.0 else "Republic"
            if winner == "Republic":
                score = 1 / score if score != 0.0 else 0.0
            score = "{:.2f}".format(score)
        else:
            winner, score = "Unknown", "Unknown"
        string += "{:^7}|{:^7}|{:^10}|{:^9}|{:^9}|{:>10}\n".format(
            start, end, match_type, match_map, score, winner)
    return string


def build_string_from_results(results: list):
    """Return a formatted string from a results list"""
    total = str()
    # name, faction, dmgd, dmgt, assists, deaths, ship
    for result in sorted(results, key=lambda item: item[1]):
        string = "{:<16}| {:<9} |{:>10} |{:>10} |{:>12} |{:>7} | {:<14}\n".format(*result)
        total += string
    return total


def build_matches_overview_string(matches: dict):
    """
    Build a string from a matches dictionary

    matches = {id_fmt: (server, start, map, score, end)}
    """
    rows = list()
    now = datetime.now()
    for (server, start, map, score, end) in matches.values():
        server = SERVER_NAMES[server]
        running = end == UNKNOWN_END
        strptime = datetime.strptime
        if running is True:
            time = (now - datetime.combine(now.date(), strptime(start, TIME_FORMAT).time()))
        else:
            time = (strptime(end, TIME_FORMAT) - strptime(start, TIME_FORMAT))
        time = int(time.total_seconds())
        state = "active" if running is True else "done"
        if map == UNKNOWN_MAP:
            type = "..."
        else:
            type, map = map.split(",")
            map = MAP_NAMES[map]
            type = type.upper()
        score = float(score)
        if score > 1.0:
            score = 1 / score
            faction = "e"
        else:
            faction = "r"
        rows.append(MATCHES_ROW.format(state, server, type, map, score, faction, time // 60))
    message = str().join(rows)
    return message


def justify_with_indent(string: str, length: int = 80, indent: int = 4)->str:
    words = string.split(" ")
    total, line = str(), str()
    for word in words:
        if len(line + word) + indent > length:
            total += " " * indent + line + "\n"
            line = str()
        line += word + " "
    if len(line) != 0:
        total += " " * indent + line
    return total


def build_upgrade_string(upgrade_str: str):
    """
    Build a human-readable string showing upgrades from an upgrade str

    123RL -> (Right, Left)
    123LR -> (Left, Right)
    123R -> (Right, None)
    123 -> (Level 3)
    12L -> (Left)
    """
    string = str()
    if len(upgrade_str) == 0:
        return "(No upgrades)"
    t_choice = None
    for upgrade in upgrade_str:
        if upgrade.isdigit():
            string = "(Level {})".format(upgrade)
            continue
        upgrade = UPGRADE_STR[upgrade]
        if t_choice is None:
            string = "({})".format(upgrade)
            t_choice = upgrade
        else:
            string = "({}, {})".format(t_choice, upgrade)
    return string
        

def build_mine_string(mine: dict):
    """
    'Mine_Armor_Penetration': 0.0,
    'Mine_Count': 1.0,
    'Mine_Crit_Chance': 0.0,
    'Mine_DOT': 0.0,
    'Mine_DOT_Damage': 0.0,
    'Mine_DOT_Duration': 0.0,
    'Mine_Damage': 0,
    'Mine_Explosion_Damage': 565,
    'Mine_Explosion_Radius': 30,
    'Mine_Hull_Damage': 1.0,
    'Mine_Lifespan': 120,
    'Mine_Range': 15,
    'Mine_Shield_Damage': 0.0,
    'Mine_Shield_Piercing': 1.0,
    'Mine_Slow': 0.0,
    'Mine_Slow_Duration': 0.0,
    'Mine_Slow_Effect': 0.0
    """
    string = \
        "*Maximum amount of mines*: {Mine_count}\n" \
        "*Lifespan*: {Mine_Lifespan}\n" \
        "*Cooldown*: {Cooldown}\n" \
        "*Trigger Radius*: {Mine_Range}\n" \
        "*Explosion Radius*: {Mine_Explosion_Radius}\n" +\
        ("*Target Damage*: {Mine_Damage}\n" if mine["Mine_Damage"] != 0.0 else "")
    if mine["Mine_Explosion_Damage_Hull"] != mine["Mine_Explosion_Damage_Shields"]:
        string += "*Explosion Damage (hull-shields)*: {Mine_Explosion_Damage_Hull}-{Mine_Explosion_Damage_Shields}p\n"
    else:
        string += "*Explosion Damage*: {Mine_Explosion_Damage}p\n"
    if "Mine_Crit_Chance" in mine and mine["Mine_Crit_Chance"] != 0.0:
        string += "*Crit Chance*: {Mine_Crit_Chance}\n"
    if "Mine_Shield_Piercing" in mine and mine["Mine_Shield_Piercing"] != 0.0:
        string += "*Shield Piercing*: {Mine_Shield_Piercing}\n"
    if "Mine_Slow" in mine and mine["Mine_Slow"] == 1.0:
        string += "*Slow Effect*: {Mine_Slow_Effect} for {Mine_Slow_Duration}\n"
    if "Mine_DOT" in mine and  mine["Mine_DOT"] == 1.0:
        string += "*DOT Effect*: {Mine_DOT_Damage} of damage over {Mine_DOT_Duration}\n"
    mine = {key: get_value_string(key, val) for key, val in mine.items()}
    return string.format(**mine)


def get_value_string(statistic: str, value: float) -> str:
    """Get a nicely formatted string with unit for a stat value"""
    if statistic not in stats.STATISTICS:
        return "{:.2f}".format(value)
    category, string, unit = stats.STATISTICS[statistic]
    if "%" in unit:
        return "{:.1f}{}".format(value * 100, unit)
    elif unit == "bool":
        return "False" if value == 0.0 else "True"
    elif unit == "p":
        return "{:.0f}{}".format(value, unit)
    elif "m/s" in unit:
        return"{:.1f}{}".format(value * 10, unit).replace("^2", "²")
    elif unit == "m":
        return "{:.0f}{}".format(value * 100, unit)
    elif unit == "i":
        return "{:.0f}".format(value)
    elif unit == "1f":
        return "{:.1f}".format(value)
    elif unit == "im":
        return "{:.0f}".format(value * 100)
    else:
        return "{:.1f}{}".format(value, unit)
