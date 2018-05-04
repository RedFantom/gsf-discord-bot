"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import os
import sys
import logging
from datetime import datetime
from hashlib import sha256
# Packages
from discord import User


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"

SERVERS = {
    "SA": "Satele Shan",
    "SF": "Star Forge",
    "TH": "Tulak Hord",
    "DM": "Darth Malgus",
    "TL": "The Leviathan"
}

STDOUT = False


def hash_auth(auth: str):
    """Securely hash an authentication code"""
    hasher = sha256()
    hasher.update(str(auth).encode("utf-8"))
    return hasher.hexdigest()


def setup_logger(name: str, file_name: str, level=logging.DEBUG)->logging.Logger:
    """Initialize a Logger with a file handler"""
    file_path = os.path.join(get_log_directory(), file_name)
    logger = logging.Logger(name, level=level)
    file = logging.FileHandler(file_path)
    stdout = logging.StreamHandler(sys.stdout)
    logger.addHandler(file if STDOUT is False else stdout)
    fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file.setFormatter(fmt)
    stdout.setFormatter(fmt)
    return logger


def get_log_directory():
    """Return an absolute path to the log directory"""
    path = os.path.join("/", "var", "log", "discord")
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_assets_directory():
    """Return an absolute path to the assets directory"""
    return os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "assets"))


def get_temp_directory():
    """Return an absolute path to a temporary directory"""
    folder = "/var/tmp/discord"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def get_temp_file(ext: str, user: User):
    """Return an absolute path to a temporary file"""
    return os.path.join(get_temp_directory(), "{}_{}.{}".format(user.name, datetime.now().strftime(TIME_FORMAT), ext))


def datetime_to_str(dt: datetime)->str:
    if isinstance(dt, str):
        return dt
    return dt.strftime(DATE_FORMAT)


def str_to_date(dt: str)->datetime:
    if isinstance(dt, datetime):
        return dt
    return datetime.strptime(dt.strip(), DATE_FORMAT)


def str_to_time(dt: str)->datetime:
    if isinstance(dt, datetime):
        return dt
    return datetime.strptime(dt.strip(), TIME_FORMAT)
