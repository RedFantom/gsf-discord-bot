"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
import os
import sys
import logging
from datetime import datetime
from hashlib import sha256


DATE_FORMAT = "%Y-%m-%d|%H:%M:%S.%f"

SERVERS = {
    "SA": "Satele Shan",
    "SF": "Star Forge",
    "TH": "Tulak Hord",
    "DM": "Darth Malgus",
    "TL": "The Leviathan"
}


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
    logger.addHandler(file)
    logger.addHandler(stdout)
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


def datetime_to_str(dt: datetime)->str:
    if isinstance(dt, str):
        return dt
    return dt.strftime(DATE_FORMAT)


def str_to_datetime(dt: str)->datetime:
    if isinstance(dt, datetime):
        return dt
    return datetime.strptime(dt.strip(), DATE_FORMAT)
