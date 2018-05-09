"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import traceback
# Project Modules
from database import DatabaseHandler
from server.server import Server


class DiscordServer(Server):
    """Asynchronous Server for GSF Parser Clients"""
    SUCCESS_MESSAGE = "ack"

    def __init__(self, database: DatabaseHandler, host: str, port: int):
        """
        :param database: DatabaseHandler instance to perform database
            operations on.
        """
        Server.__init__(self, database, host, port, "DiscordServer")

    def process_command(self, command: str, args: tuple):
        """Process a command given by a Client"""
        try:
            if command == "match":
                self.process_match_start(*args)
            elif command == "result":
                self.process_result(*args)
            elif command == "score":
                self.process_score(*args)
            elif command == "map":
                self.process_map(*args)
            elif command == "end":
                self.process_end(*args)
            elif command == "character":
                self.process_character(*args)
            else:
                self.logger.error("Invalid command received: {}.".format(command))
        except Exception:
            self.logger.error("Error occurred during processing of command `{}, {}`\n{}".format(
                command, args, traceback.format_exc()))
            return None
        return DiscordServer.SUCCESS_MESSAGE

    def process_match_start(self, server: str, date: str, time: str, id_fmt: str):
        """Insert a new match into the database"""
        self.logger.debug("Inserting new match into database: {}, {}".format(server, time))
        self.db.insert_match(server, date, time, id_fmt)

    def process_result(self, server: str, date: str, start: str, id_fmt: str, character: str,
                       assists: str, dmgd: str, dmgt: str, deaths: str, ship: str):
        """Insert a character result into the database"""
        self.logger.debug("Inserting new result into database: {}".format((
            server, start, character, assists, dmgd, dmgt, deaths)))
        assists, dmgd, dmgt, deaths = map(int, (assists, dmgd, dmgt, deaths))
        self.db.insert_result(character, server, date, start, id_fmt, assists, dmgd, dmgt, deaths, ship)

    def process_map(self, server: str, date: str, start: str, id_fmt: str, map: str):
        """Insert the map of a match into the database"""
        self.logger.debug("Updating map in database: {}".format(server, start, map))
        map_eval = map.split(",")
        if not isinstance(map_eval, list) or not len(map_eval) == 2:
            self.logger.error("Invalid map tuple received: {}.".format(map_eval))
            return False
        self.db.update_match(server, date, start, id_fmt, map=map)

    def process_score(self, server: str, date: str, start: str, id_fmt: str, score: str):
        """Insert the score of a match into the database"""
        self.logger.debug("Updating score in database: {}".format(server, start, score))
        if not score.isdecimal():
            self.logger.error("Invalid literal for float.")
            return
        score = float(score)
        self.db.update_match(server, date, start, id_fmt, score=score)

    def process_end(self, server: str, date: str, start: str, id_fmt: str, end: str):
        """Insert the end time of a match into the database"""
        self.logger.debug("Updating end in database: {}".format(server, start, end))
        self.db.update_match(server, date, start, id_fmt, end=end)

    def process_character(self, server: str, faction: str, name: str, discord: str):
        """Insert a new character into the database for a Discord user"""
        self.logger.debug("Inserting new character into dtaabase: {}".format(
            server, faction, name, discord))
        self.db.insert_character(name, server, faction, discord)