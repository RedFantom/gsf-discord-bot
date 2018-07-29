"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import ast
import os
import configparser


def config_eval(value):
    """
    Safely evaluate a string that can be a in a configuration file to a
    valid Python value. Performs error handling and checks special
    cases.
    """
    try:
        literal = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value
    if literal == 1:
        return True
    elif literal == 0:
        return False
    else:
        return literal


class SettingsDict(dict):
    def __getitem__(self, item):
        return config_eval(dict.get(self, item))


class Settings(object):
    """
    Class that provides an interface to a ConfigParser instance. The
    file parsed by the ConfigParser contains the settings for the GSF
    Parser. The settings interface is a safe one that provides backwards
    compatibility and uses a custom evaluation function to safely
    evaluate the settings to a valid Python value.
    """
    def __init__(self, file_name="settings.ini"):
        """
        :param file_name: Settings file filename
        """
        self.file_name = file_name
        if not os.path.exists(self.file_name):
            raise FileNotFoundError("{} does not exist in working directory".format(file_name))
        self.conf = configparser.ConfigParser()
        self.settings = dict()
        self.read_settings()

    def read_settings(self):
        """
        Read the settings from the settings file using a ConfigParser
        and store them in the instance attribute so they can be
        retrieved using the __getitem__ function.
        """
        self.settings.clear()
        with open(self.file_name, "r") as fi:
            self.conf.read_file(fi)
        for section in self.conf.sections():
            self.settings[section] = SettingsDict()
            self.settings[section].update(self.conf[section])

    def __getitem__(self, section):
        """
        Returns a SettingsDictionary for a section key. Also provides
        error handling for when the section is not found.
        """
        if section not in self.settings:
            raise KeyError("Incomplete settings file is missing section '{}'".format(section))
        return self.settings[section]

    def __contains__(self, item):
        return item in self.settings

    def dict(self):
        """Build a dictionary from self and return a copy"""
        return dict(self.settings).copy()
