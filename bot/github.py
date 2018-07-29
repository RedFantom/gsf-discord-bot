"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
import os
# Packages
from github import Github, GithubException
from semantic_version import Version
# Project Modules
from bot.embeds import embed_from_release
from settings import settings


BASE_LINK = "https://github.com/%s/%s/releases/download/{tag}/GSF_Parser_{tag}.{ext}" \
    % (settings["github"]["user"], settings["github"]["repo"])
EXTENSIONS = ("exe", "zip")


class VersionTracker(object):
    def __init__(self):
        if not os.path.exists("latest"):
            with open("latest", "w") as fo:
                fo.write("None")
        with open("latest") as fi:
            self.version = fi.read().strip()
        if self.version == "None":
            self.set("v5.0.0")

    def set(self, version: str):
        with open("latest", "w") as fo:
            fo.write(version)
        self.version = version

    def get(self):
        return self.version

    def __str__(self):
        return self.version[1:]


latest = VersionTracker()


async def get_download_link()->(tuple, None):
    """
    Build download link to the most recent version of the GSF Parser

    Download the tags from the GitHub repository and select the most
    recent one. Then the download links are built based on that. Returns
    a tuple that can be passed directly to the GITHUB_LINKS message
    formatter.
    """
    version = get_latest_tag()
    if version is None:
        return None
    tag = "v{}.{}.{}".format(version.major, version.minor, version.patch)
    links = list()
    for ext in EXTENSIONS:
        links.append(BASE_LINK.format(tag=tag, ext=ext))
    return (tag,) + tuple(links)


def get_latest_tag()->(None, Version):
    """Return the latest Version of the GSF Parser"""
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
    return version


async def github_monitor(self):
    """Monitor the release of a new version of the GSF Parser"""
    global latest
    if settings["github"]["monitor"] is False:
        return
    name, repo = settings["github"]["user"], settings["github"]["repo"]
    try:
        latest = get_latest_tag()
        self.logger.debug("Latest tag: {}".format(latest))
        repo = Github().get_user(name).get_repo(repo)
        releases = repo.get_releases()
        for release in releases:
            if release.draft is True:
                continue
            try:
                version = Version(release.tag_name[1:])
            except ValueError:
                continue
            if version != latest or version == Version(str(latest)):
                self.logger.debug("{} rejected.".format(version))
                continue
            embed = embed_from_release(release)
            for channel in self.validated_channels:
                await self.bot.send_message(channel, embed=embed)
            latest.set(release.tag_name)
    except Exception as e:
        self.raven.captureException()
        context = {"exception": e, "message": "Exception in github_monitor"}
        self.exception_handler(self.loop, context)
        return
    await asyncio.sleep(1800)
    self.loop.create_task(self.github_monitor())
