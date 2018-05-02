"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
from ast import literal_eval
import traceback
# Project Modules
from utils import setup_logger
from database import DatabaseHandler
from utils import hash_auth


class Server(object):
    """Asynchronous Server for GSF Parser Clients"""

    def __init__(self, database: DatabaseHandler, host: str, port: int):
        """
        :param database: DatabaseHandler instance to perform database operations
        """
        self.logger = setup_logger("ClientHandler", "server.log")
        self.db = database
        self.host, self.port = host, port

    async def start(self):
        host, port = self.host, self.port
        self.logger.info("Initializing server ({}, {})".format(host, port))
        await asyncio.start_server(self.handle_client, host, port)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a single Client that wants to send a command"""
        try:
            data, count = "", 0
            self.logger.debug("Client accepted.")
            while len(data) == 0:
                await asyncio.sleep(0.1)
                data = await reader.read(100)
                data = data.decode().replace("+", "")
                if count > 20:
                    self.logger.debug("Did not receive any data from client.")
                    return
            self.logger.debug("Data read: {}".format(data))
            self.logger.debug("Received message from client: {}".format(data.strip()))
            elements = data.split("_")
            try:
                (discord, auth, command), args = elements[0:3], tuple(elements[3:])
            except ValueError:
                self.logger.error("Invalid amount of elements: {}".format(elements))
                return
            if self.authenticate(discord, auth) is False:
                self.logger.info("User {} failed to authenticate.".format(discord))
                writer.write(b"unauth")
            else:
                self.logger.debug("User {} successfully authenticated.".format(discord))
                try:
                    self.process_command(command, args)
                except Exception:
                    self.logger.error("Error occurred while processing command: {}".format(traceback.format_exc()))
                    writer.write(b"error")
                    await writer.drain()
                    writer.close()
                    return
                writer.write(b"ack")
                self.logger.debug("Request complete, sent acknowledgement.")
            await writer.drain()
            writer.close()
        except Exception:
            self.logger.error("Error occurred while processing client: {}".format(traceback.format_exc()))

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
            return False
        return True

    def authenticate(self, discord: str, auth: str):
        """Authenticate the user that gives the command"""
        code = self.db.get_auth_code(discord)
        return code == hash_auth(auth)

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
        map_eval = literal_eval(map)
        if not isinstance(map_eval, tuple) and len(map_eval) == 2:
            self.logger.error("Invalid map tuple received: {}.".format(map_eval))
            return False
        self.db.update_match(server, date, start, id_fmt, map=map)

    def process_score(self, server: str, date: str, start: str, id_fmt: str, score: str):
        """Insert the score of a match into the database"""
        self.logger.debug("Updating score in database: {}".format(server, start, score))
        if len(score.split("-")) != 2:
            self.logger.error("Invalid score tuple received: {}.".format(score))
            return False
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
