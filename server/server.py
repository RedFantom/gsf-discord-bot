"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
import asyncio
from ast import literal_eval
# Project Modules
from utils import setup_logger, str_to_datetime
from database import DatabaseHandler
from database import select


class Server(object):
    """Asynchronous Server for GSF Parser Clients"""

    def __init__(self, database: DatabaseHandler, host: str, port: int):
        """
        :param database: DatabaseHandler instance to perform database operations
        """
        self.logger = setup_logger("ClientHandler", "server.log")
        self.db = database
        asyncio.start_server(self.handle_client, host, port)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a single Client that wants to send a command"""
        data = await reader.read().decode()
        self.logger.debug("Received message from client: {}".format(data))
        writer.write("ack")
        await writer.drain()
        self.process_data(data)
        writer.close()

    def process_data(self, data: str):
        """Process the data received from a Client"""
        elements = data.split("_")
        (discord, auth, command), args = elements[0:3], tuple(elements[3:])
        if self.authenticate(discord, auth) is False:
            self.logger.info("User {} failed to authenticate.")
            return
        self.logger.debug("User {} successfully authenticated.")
        self.process_command(command, args)

    def process_command(self, command: str, args: tuple):
        """Process a command given by a Client"""
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

    def authenticate(self, discord: str, auth: str):
        """Authenticate the user that gives the command"""
        code = self.db.exec_query(select.GET_AUTH_CODE.format(discord))[0][0]
        return code == auth

    def process_match_start(self, server: str, time: str):
        """Insert a new match into the database"""
        time = str_to_datetime(time)
        self.db.insert_match(server, time)

    def process_result(self, server: str, start: str, character: str,
                       assists: str, damage: str, deaths: str):
        """Insert a character result into the database"""
        start = str_to_datetime(start)
        assists, damage, deaths = map(int, (assists, damage, deaths))
        self.db.insert_result(character, server, start, assists, damage, deaths)

    def process_map(self, server: str, start: str, map: str):
        """Insert the map of a match into the database"""
        map_eval = literal_eval(map)
        if not isinstance(map_eval, tuple) and len(map_eval) == 2:
            self.logger.error("Invalid map tuple received: {}.".format(map_eval))
            return False
        start = str_to_datetime(start)
        self.db.update_match(start, server, map=map)

    def process_score(self, server: str, start: str, score: str):
        """Insert the score of a match into the database"""
        start = str_to_datetime(start)
        if len(score.split("-")) != 2:
            self.logger.error("Invalid score tuple received: {}.".format(score))
            return False
        self.db.update_match(start, server, score=score)

    def process_end(self, server: str, start: str, end: str):
        """Insert the end time of a match into the database"""
        start, end = map(str_to_datetime, (start, end))
        self.db.update_match(start, server, end=end)

    def process_character(self, server: str, faction: str, name: str, discord: str):
        """Insert a new character into the database for a Discord user"""
        self.db.insert_character(name, server, faction, discord)
