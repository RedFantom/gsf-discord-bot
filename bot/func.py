"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from io import BytesIO
# Packages
from github import Github, GithubException
from PIL import Image
import requests
from semantic_version import Version
# Project Modules
from database.servers import SERVERS


BASE_LINK = "https://github.com/RedFantom/gsf-parser/releases/download/{tag}/GSF_Parser_{tag}.{ext}"
EXTENSIONS = (".exe", ".zip")


async def get_server_status():
    """
    Return a dictionary of server statuses

    Downloads the page and parses it by searching for two specific
    patterns:
    - <class="name"> - For the server name - Full server names
    - <class="status"> - For the server status - UP or DOWN
    """
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


async def download_image(link: str)->Image.Image:
    """
    Download file found in the link and return the Image found there

    Asynchronous wrapper around the functions required to download and
    open an Image from a link. Opens the Image by using BytesIO which
    offers the same interface as a file buffer created with open().
    """
    return Image.open(BytesIO(requests.get(link).content))


async def get_download_link()->(tuple, None):
    """Build download link to the most recent version of the GSF Parser"""
    github = Github()
    user = github.get_user("RedFantom")
    repo = user.get_repo("gsf-parser")
    try:
        tags = repo.get_tags()
    except GithubException:
        return None
    versions = list()
    for tag in tags:
        tag = tag.name[1:].replace("beta", "").replace("alpha", "").replace("_", "")
        try:
            versions.append(Version(tag))
        except ValueError:
            continue
    version = max(versions)
    tag = "v{}.{}.{}".format(version.major, version.minor, version.path)
    links = list()
    for ext in EXTENSIONS:
        links.append(BASE_LINK.format(tag=tag, ext=ext))
    return (tag,) + tuple(links)