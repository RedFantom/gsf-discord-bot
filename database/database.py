"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from threading import Lock
import sqlite3 as sql
import logging
from contextlib import closing
from datetime import datetime
# Project Modules
from database import create, insert, select
from utils import setup_logger, datetime_to_str


class DatabaseHandler(object):
    """
    Thread-safe database handler to allow the processing of queries
    of multiple clients. Uses a Lock to make sure that only a single
    call can be executed on the database at the same time.
    """

    def __init__(self, file_name="database.db", log_level=logging.DEBUG):
        """
        :param file_name: File name for the SQLite database
        :param log_level: Logger logging level
        """
        # Attributes
        self._db = None
        self._file_name = file_name
        self._db_lock = Lock()
        # Build logger
        self.logger = setup_logger("DatabaseHandler", "database.log", level=log_level)
        self.debug, self.info, self.error = self.logger.debug, self.logger.info, self.logger.error
        # Initialize the database
        self.init_db()

    def init_db(self):
        """Initialize the database connection and tables"""
        self._db = sql.connect(self._file_name)
        for table in ["SERVER", "USER", "CHARACTER", "MATCH", "RESULT"]:
            command = getattr(create, "CREATE_TABLE_{}".format(table))
            try:
                self.exec_command(command)
                self.debug("Created table {}.".format(table))
            except sql.OperationalError:
                self.error("Failed to create table {}".format(table))
                raise
        self.exec_command(insert.INSERT_SERVERS)
        return True

    def exec_command(self, command: str):
        """Execute a command on the database"""
        self._db_lock.acquire()
        with self.cursor as cursor:
            cursor.execute(command)
            self.debug("Executed command: {}".format(command))
        self._db_lock.release()

    def exec_query(self, query: str):
        """Execute a query on the database and return results"""
        self._db_lock.acquire()
        with self.cursor as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            self.debug("Executed query: {}".format(query))
            self.debug("Query results: {}".format(results))
        self._db_lock.release()
        return results

    @property
    def db(self) -> sql.Connection:
        return self._db

    @property
    def cursor(self) -> sql.Cursor:
        """Return cursor that allows usage in with-clause"""
        cursor = self.db.cursor()
        return closing(cursor)

    def insert_character(self, name: str, server: str, faction: str, owner: str):
        """Insert a new character into the database"""
        command = insert.INSERT_CHARACTER.format(name=name, server=server, faction=faction, owner=owner)
        self.exec_command(command)

    def insert_user(self, user_id: str, home: str = None):
        """Insert a new Discord user into the database"""
        command = insert.INSERT_USER.format(user_id)
        if home is None:
            command = insert.INSERT_USER_HOME.format(user_id, home)
        self.exec_command(command)

    def insert_match(self, server: str, start: (datetime, str)):
        """Insert a new match into the database"""
        start = datetime_to_str(start)
        command = insert.INSERT_MATCH.format(server=server, start=start)
        self.exec_command(command)

    def update_match(self, start: datetime, server: str,
                     score: str = None, map: str = None, end: datetime = None):
        """Insert the match score into the database"""
        commands = list()
        if score is not None:
            commands.append(insert.UPDATE_MATCH_SCORE.format(score=score, start=start, server=server))
        if end is not None:
            end = datetime_to_str(end)
            commands.append(insert.UPDATE_MATCH_END.format(end=end, start=start, server=server))
        if map is not None:
            commands.append(insert.UPDATE_MATCH_MAP.format(map=map, start=start, server=server))
        for command in commands:
            self.exec_command(command)

    def insert_result(self, character: str, server: str, start: datetime,
                      assists: int, damage: int, deaths: int):
        """Insert the result of a given character into the database"""
        start = datetime_to_str(start)
        self.debug("Inserting result of {} on server {} for match start {}.".format(character, server, start))
        query = select.GET_CHARACTER_ID.format(name=character, server=server)
        result = self.exec_query(query)
        if len(result) == 0:
            self.error("Character '{}' is not known on this server '{}'.".format(character, server))
            return False
        character_id = result[0][0]
        query = select.GET_MATCH_ID.format(server=server, start=start)
        result = self.exec_query(query)
        if len(result) == 0:
            self.insert_match(server, start)
            result = self.exec_query(query)
        match_id = result[0][0]
        command = insert.INSERT_RESULT.format(
            match=match_id, char=character_id, assists=assists, damage=damage, deaths=deaths)
        self.exec_command(command)

    def get_auth_code(self, discord: str):
        """Return the authentication code for a given Discord user"""
        result = self.exec_query(select.GET_AUTH_CODE.format(discord=discord))
        if result == 0:
            return None
        auth, = result[0]
        return auth
