"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Project Modules
from database.servers import SERVER_NAMES


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
                score = 1 / score
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
