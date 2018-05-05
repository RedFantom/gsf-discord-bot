"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
# Packages
import requests
# Project Modules
from database.servers import SERVERS


async def get_server_status():
    """Return a dictionary of server statuses"""
    try:
        page = requests.get("http://www.swtor.com/server-status")
    except (requests.ConnectionError, requests.HTTPError):
        return None
    lines = page.content.decode().split("\n")
    servers = {}
    status = None
    for line in lines:
        if "class=\"name\"" in line:
            server = line.split(">")[1].split("<")[0].lower().replace(" ", "_")
            servers[server] = status
        if "class=\"status\"" in line:
            status = line.split(">")[2].split("<")[0].lower().replace("up", "online").replace("down", "offline")
    for server in SERVERS:
        if server in servers:
            continue
        servers[server] = "offline"
    return servers
