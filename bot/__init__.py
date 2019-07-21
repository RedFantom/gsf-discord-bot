"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""


class DiscordBotException(ValueError):
    message = ""

    def __init__(self, message, *args):
        self.message = message
        ValueError.__init__(self, *args)
