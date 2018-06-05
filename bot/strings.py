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
from data.components import component_strings, component_types, component_keys
from parsing.ships import Ship, Component
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


async def build_string_from_ship(ship: Ship, name: str):
    message = "```markdown\n{}\n```"
    string = "# {} ({})\n\nComponents:\n{}\nCrew:\n{}\n"
    components, crew = str(), str()
    for category in component_keys:
        component = ship.components[category]
        if component is None or not isinstance(component, Component):
            continue
        components += "- {} {}\n".format(
            component.name,
            build_upgrade_string(
                ship.build_upgrade_string(
                    component.upgrades, component.type)))
    for role, member in ship.crew.items():
        if member is None:
            crew += "- {}: Unknown\n".format(role)
            continue
        _, _, member = member
        crew += "- {}: {}\n".format(role, member)
    string = string.format(name, ship.name, components, crew)
    return message.format(string)


async def build_string_from_crew_dict(crew_dict: dict) -> str:
    """
    Build a human readable message string from a crew member dictionary
    """
    message = "```markdown\n{} ({})\n```"
    string = "# {}\n" \
             "Ability: {}\n" \
             "{}\n\n" \
             "Passive: {}\n" \
             "{}\n\n" \
             "Passive: {}\n" \
             "{}\n"
    role = crew_dict["Category"]
    name = crew_dict["Name"]
    ability = crew_dict["AbilityName"]
    passive1 = crew_dict["PassiveName"]
    passive2 = crew_dict["SecondaryPassiveName"]
    abilityd = crew_dict["AbilityDescription"]
    passive1d = crew_dict["PassiveDescription"]
    passive2d = crew_dict["SecondaryPassiveDescription"]
    string = string.format(
        name, role, ability, justify_with_indent(abilityd),
        passive1, justify_with_indent(passive1d),
        passive2, justify_with_indent(passive2d))
    return message.format(string)


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
        

