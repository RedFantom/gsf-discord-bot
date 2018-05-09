"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
from datetime import datetime, timedelta
import traceback
# Project Modules
from database import DatabaseHandler
from server.server import Server
from utils.utils import DATE_FORMAT, TIME_FORMAT
from utils import UNKNOWN_MAP, UNKNOWN_END, UNKNOWN_SCORE


class DiscordServer(Server):
    """Asynchronous Server for GSF Parser Clients"""
    SUCCESS_MESSAGE = "ack"
    MATCH_END_TIME = 120

    def __init__(self, database: DatabaseHandler, loop: asyncio.BaseEventLoop, host: str, port: int):
        """
        :param database: DatabaseHandler instance to perform database
            operations on.
        """
        Server.__init__(self, database, host, port, "DiscordServer")
        self.matches = dict()
        self.queue = list()
        self.loop = loop
        self.loop.create_task(self.process_matches())

    async def process_matches(self):
        """Process matches in the queue"""
        while True:
            try:
                today = datetime.now().strftime(DATE_FORMAT)
                for command, args in self.queue:
                    self.logger.debug("Process matches processing: {}, {}".format(command, args))
                    if command == "start":  # New match
                        self.logger.debug("Processing new match.")
                        server, date, start, id_fmt = args
                        if id_fmt in self.matches or date != today:
                            self.logger.debug("Match is not today.")
                            continue
                        self.matches[id_fmt] = (server, start, UNKNOWN_MAP, UNKNOWN_SCORE, UNKNOWN_END)
                    elif command == "end":  # Match end
                        self.logger.debug("Processing match end.")
                        server, date, start, id_fmt, new_end = args
                        if id_fmt not in self.matches:
                            self.matches[id_fmt] = (server, start, UNKNOWN_MAP, UNKNOWN_SCORE, new_end)
                            continue
                        server, start, mmap, score, end = self.matches[id_fmt]
                        if end != UNKNOWN_END:
                            continue
                        self.matches[id_fmt] = server, start, mmap, score, new_end
                    elif command == "map":  # Map update
                        self.logger.debug("Processing map update.")
                        server, date, start, id_fmt, new_map = args
                        if id_fmt not in self.matches:
                            self.matches[id_fmt] = (server, start, new_map, UNKNOWN_SCORE, UNKNOWN_END)
                            continue
                        server, start, mmap, score, end = self.matches[id_fmt]
                        if mmap != UNKNOWN_MAP:
                            continue
                        self.matches[id_fmt] = (server, start, new_map, score, end)
                    elif command == "score":  # Score update
                        self.logger.debug("Processing score update.")
                        server, date, start, id_fmt, score = args
                        if id_fmt not in self.matches:
                            self.matches[id_fmt] = (server, start, UNKNOWN_MAP, score, UNKNOWN_END)
                            continue
                        server, start, mmap, _, end = self.matches[id_fmt]
                        self.matches[id_fmt] = (server, start, mmap, score, end)
                    # Others are ignored
                for id_fmt, (_, start, _, _, end) in self.matches.copy().items():
                    # Remove all matches that have been over for a while
                    now = datetime.now()
                    projected = datetime.strptime(start, TIME_FORMAT) + timedelta(minutes=14)
                    if end != UNKNOWN_END:
                        projected = datetime.strptime(end, TIME_FORMAT)
                    if (now - projected).total_seconds() > self.MATCH_END_TIME:
                        del self.matches[id_fmt]
                self.queue.clear()
            except Exception:
                self.logger.error("An error occurred while processing queue:\n{}".format(traceback.format_exc()))
            self.logger.debug("Process matches yielded {} matches".format(len(self.matches)))
            await asyncio.sleep(1)

    async def process_command(self, command: str, args: tuple):
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
            self.queue.append((command, args))
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
        self.logger.debug("Updating score in database: {}, {}, {}".format(server, start, score))
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
