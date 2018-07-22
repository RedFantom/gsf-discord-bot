"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from contextlib import closing
from datetime import datetime, timedelta
import sqlite3 as sql
from threading import Lock
# Project Modules
from database import create, insert, select, delete
from data.servers import SERVER_NAMES
from parsing.ships import Ship
from parsing.strategies import Strategy
from utils import setup_logger
from utils.utils import DATE_FORMAT


class DatabaseHandler(object):
    """
    Thread-safe database handler to allow the processing of queries
    of multiple clients. Uses a Lock to make sure that only a single
    call can be executed on the database at the same time.
    """

    def __init__(self, file_name="database.db"):
        """
        :param file_name: File name for the SQLite database
        """
        # Attributes
        self._db = None
        self._file_name = file_name
        self._db_lock = Lock()
        # Build logger
        self.logger = setup_logger("DatabaseHandler", "database.log")
        self.debug, self.info, self.error = self.logger.debug, self.logger.info, self.logger.error
        # Initialize the database
        self.init_db()

    def init_db(self):
        """Initialize the database connection and tables"""
        self._db = sql.connect(self._file_name)
        for table in ["SERVER", "USER", "CHARACTER", "MATCH", "RESULT", "BUILDS", "STRATEGIES"]:
            command = getattr(create, "CREATE_TABLE_{}".format(table))
            try:
                self.exec_command(command)
                self.info("Created table {}.".format(table))
            except sql.OperationalError:
                self.error("Failed to create table {}".format(table))
                raise
        self.exec_command(insert.INSERT_SERVERS)
        return True

    def exec_command(self, command: str, *args):
        """Execute a command on the database"""
        self.debug("Acquiring database lock.")
        self._db_lock.acquire()
        try:
            with self.cursor as cursor:
                self.debug("Executing command: {}".format(command))
                cursor.execute(command, *args)
                self.debug("Executed command: {}".format(command))
            r = True
        except sql.OperationalError as e:
            self.logger.error("Execution of command failed: {}.".format(e))
            r = False
        self.db.commit()
        self._db_lock.release()
        self.debug("Database lock released.")
        return r

    def exec_query(self, query: str):
        """Execute a query on the database and return results"""
        self._db_lock.acquire()
        with self.cursor as cursor:
            self.debug("Executing query: {}".format(query))
            cursor.execute(query)
            results = cursor.fetchall()
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

    def insert_user(self, user_id: str, code: str):
        """Insert a new Discord user into the database"""
        self.info("Inserting a new user into the Database: {}".format(user_id))
        date = datetime.now().strftime(DATE_FORMAT)
        command = insert.INSERT_USER.format(discord=user_id, code=code, last=date)
        self.exec_command(command)

    def update_auth_code(self, user_id: str, code: str):
        """Update the authentication code of a user in the database"""
        self.info("Updating authentication code of {}.".format(user_id))
        command = insert.UPDATE_CODE.format(discord=user_id, code=code)
        self.exec_command(command)

    def update_user_date(self, user_id: str, date: str):
        """Update the date the user last inserted data into the database"""
        if isinstance(date, datetime):
            date = datetime.strftime(date, DATE_FORMAT)
        self.info("Updating the date {} last inserted data to {}".format(user_id, date))
        command = insert.UPDATE_USER_LAST.format(tag=user_id, date=date)
        self.exec_command(command)

    def insert_match(self, server: str, date: str, start: str, id_fmt: str):
        """Insert a new match into the database"""
        command = insert.INSERT_MATCH.format(
            server=server, start=start, date=date, idfmt=id_fmt)
        self.exec_command(command)

    def update_match(self, server: str, date: str, start: str, id_fmt: str,
                     score: float = None, map: str = None, end: str = None):
        """Insert the match score into the database"""
        if self.get_match_id(server, date, id_fmt) is None:
            self.logger.debug("Match {}, {}, {} was not in database, inserting now...")
            self.insert_match(server, date, start, id_fmt)
        match = self.get_match_id(server, date, id_fmt)
        commands = list()
        kwargs = {
            "match": match,
            "map": map,
            "score": score,
            "end": end
        }
        if score is not None:
            commands.append(insert.UPDATE_MATCH_SCORE.format(**kwargs))
        if end is not None:
            commands.append(insert.UPDATE_MATCH_END.format(**kwargs))
        if map is not None:
            commands.append(insert.UPDATE_MATCH_MAP.format(**kwargs))
        for command in commands:
            self.exec_command(command)

    def insert_result(self, character: str, server: str, date: str, start: str, id_fmt: str,
                      assists: int, dmgd: int, dmgt: int, deaths: int, ship: str):
        """Insert the result of a given character into the database"""
        self.debug("Inserting result of {} on server {} for match start {}.".format(character, server, start))
        char = self.get_character_id(server, character)
        if char is None:
            self.error("Character '{}' is not known on this server '{}'.".format(character, server))
            return False
        match_id = self.get_match_id(server, date, id_fmt)
        if match_id is None:
            self.insert_match(server, date, start, id_fmt)
            match_id = self.get_match_id(server, date, id_fmt)
        command = insert.INSERT_RESULT.format(
            match=match_id, char=char, assists=assists, dmgd=dmgd, dmgt=dmgt, deaths=deaths, ship=ship)
        self.exec_command(command)

    def insert_build(self, owner: str, name: str, data: str, public: bool) -> (int, None):
        """Insert a new build into the database"""
        if self.get_build_id(name, owner, required=False) is not None:
            return None
        self.exec_command(insert.INSERT_BUILD.format(owner=owner, name=name, public=int(public), data=data))
        return self.get_build_id(name, owner)

    def update_build_data(self, build: (int, str), data: str):
        """Update an existing build in the database"""
        self.exec_command(insert.UPDATE_BUILD_DATA.format(build=build, data=data))

    def update_build_public(self, build: (int, str), public: bool):
        self.exec_command(insert.UPDATE_BUILD_PUBLIC.format(build=build, public=int(public)))

    def get_match_id(self, server: str, date: str, id_fmt: str):
        """Return the match ID from the database"""
        self.logger.debug("Retrieving match id: {}, {}, {}".format(server, date, id_fmt))
        query = select.GET_MATCH_ID.format(server=server, date=date, idfmt=id_fmt)
        result = self.exec_query(query)
        if len(result) == 0:
            return None
        match, = result[0]
        return match

    def get_character_id(self, server, name):
        """Return the ID of a given character"""
        query = select.GET_CHARACTER_ID.format(name=name, server=server)
        result = self.exec_query(query)
        if len(result) == 0:
            return None
        char, = result[0]
        return char

    def get_auth_code(self, discord: str):
        """Return the authentication code for a given Discord user"""
        result = self.exec_query(select.GET_AUTH_CODE.format(discord=discord))
        if len(result) == 0:
            return None
        auth, = result[0]
        return auth

    def get_character_ids(self, discord: str):
        """Return a list of all character IDs of a Discord user"""
        result = self.exec_query(select.GET_CHARACTER_IDS.format(discord_id=discord))
        characters = list()
        for char, in result:
            characters.append(char)
        return characters

    def delete_user(self, tag: str):
        """Delete a Discord User from the database"""
        self.logger.info("Removing {} from database.".format(tag))
        characters = self.get_character_ids(tag)
        for character in characters:
            self.exec_command(delete.DELETE_RESULTS_CHARACTER.format(char_id=character))
        self.exec_command(delete.DELETE_CHARACTERS.format(discord_id=tag))
        self.exec_command(delete.DELETE_USER.format(discord_id=tag))

    def get_user_in_database(self, tag: str) -> bool:
        """Return whether a certain Discord user is in the database"""
        result = self.exec_query(select.GET_USER_ID.format(discord_id=tag))
        return len(result) != 0

    def get_user_accessed_valid(self, tag: str):
        """Return whether the user has contributed data recently enough"""
        result = self.exec_query(select.GET_USER_LAST.format(discord=tag))
        if len(result) == 0:
            return None
        last = datetime.strptime(result[0][0], DATE_FORMAT)
        today = datetime.now()
        return (today - last).days < 14

    def get_character_owner(self, server: str, name: str):
        """Return the owner tag of a given character"""
        result = self.exec_query(select.GET_CHARACTER_OWNER.format(name=name, server=server))
        if len(result) == 0:
            return None
        tag, = result[0]
        return tag

    def get_server_in_database(self, server: str):
        """Return whether a server is present in the database"""
        query = "SELECT id FROM Server WHERE 'name' = '{server}' OR id = '{server}';".format(
            server=server)
        result = self.exec_query(query)
        return len(result) != 0

    def get_matches_count_by_day(self, day: (datetime, str)):
        """Return a dictionary of server: match_count"""
        day = day.strftime(DATE_FORMAT) if isinstance(day, datetime) else day
        query = select.GET_MATCHES_COUNT_FOR_DAY_BY_SERVER.format(date=day)
        results = self.exec_query(query)
        servers = dict()
        for server, count in results:
            servers[server] = count
        return servers

    def get_matches_count_by_period(self, start: datetime, end: datetime):
        """Return a dictionary of server: match_count for a given period"""
        servers = {server: 0 for server in SERVER_NAMES.keys()}
        while start < end:
            match_count = self.get_matches_count_by_day(start)
            for server in servers.keys():
                servers[server] += match_count[server] if server in match_count else 0
            start += timedelta(days=1)
        return servers

    def get_matches_count_by_week(self):
        """Return a dictionary of server: match_count for this week"""
        today = datetime.now().date()
        servers = {server: 0 for server in SERVER_NAMES.keys()}
        for i in range(7):
            current = today - timedelta(days=i)
            match_count = self.get_matches_count_by_day(current)
            for server in servers.keys():
                servers[server] += match_count[server] if server in match_count else 0
        return servers

    def get_matches_by_day_by_server(self, server: str, date: str):
        """Return a list of matches for a given server"""
        return self.exec_query(select.GET_MATCHES_FOR_DAY_FOR_SERVER.format(server=server, date=date))

    def get_match_results(self, server: str, date: str, start: str):
        """Return the results of players participating in a match"""
        return self.exec_query(select.GET_MATCH_RESULTS.format(server=server, date=date, start=start))

    def get_build_id(self, name: str, owner: str, required=True):
        """Return the build ID and whether its public"""
        if name.isdigit():
            name = int(name)
            results = self.exec_query(select.GET_BUILD_BY_ID.format(build=name))
        else:
            results = self.exec_query(select.GET_BUILD_BY_NAME.format(name=name, owner=owner))
        if len(results) == 0:
            if not required:
                return None
            raise ValueError("I cannot find that build. Have you used a number identifier if it is not your own build?")
        if len(results) > 1:
            self.logger.error("Major issue detected: two builds with the same name and owner exist: {}, {}".
                              format(name, owner))
            raise RuntimeError("This is a design flaw.")
        build, _ = results[0]
        return build

    def get_build_data(self, build: (int, str)) -> (None, Ship):
        """Return the data (bytes) of a build"""
        if isinstance(build, str):
            build = int(build)
        results = self.exec_query(select.GET_BUILD_DATA.format(build=build))
        if len(results) == 0:
            return None
        data, = results[0]
        return data

    def get_build_owner(self, build: (int, str)):
        """Return the tag of the build owner"""
        if isinstance(build, str):
            build = int(build)
        results = self.exec_query(select.GET_BUILD_OWNER.format(build=build))
        if len(results) == 0:
            raise ValueError("That build does not exist.")
        tag, = results[0]
        return tag

    def check_build_owner(self, build: (int, str), owner: str) -> bool:
        return self.get_build_owner(build) == owner

    def build_read_access(self, build: (int, str), user: str):
        public = self.exec_query(select.GET_BUILD_PUBLIC.format(build=build))
        if len(public) == 0:
            raise ValueError("That build does not exist.")
        public, = public[0]
        owner = self.get_build_owner(build)
        return owner == user or public

    def get_public_builds(self) -> list:
        """Return all public builds in (build, name, data)"""
        results = self.exec_query(select.GET_BUILDS_PUBLIC)
        for result in results:
            build, name, data = result
            yield build, name, data

    def get_builds_owner(self, owner: str):
        """Return all builds of an owner in (build, name, data, public)"""
        results = self.exec_query(select.GET_BUILDS_BY_OWNER.format(owner=owner))
        for result in results:
            build, name, data, public = result
            yield build, name, data, public

    def get_build_name(self, name: str, owner: str):
        """Return the name of a build"""
        build = int(name) if name.isdigit() else self.get_build_id(name, owner)
        if build is None:
            raise ValueError("Invalid identifier or this build does not exist")
        if not self.build_read_access(build, owner):
            raise PermissionError("You do not have read access to that build.")
        return self.get_build_name_id(build)

    def get_build_name_id(self, build):
        results = self.exec_query(select.GET_BUILD_NAME.format(build=build))
        if len(results) == 0:
            raise ValueError("That build does not exist.")
        name, = results[0]
        return name

    def delete_build(self, build: (int, str), owner: str):
        """Delete a build by a unique identifier"""
        if isinstance(build, str) and not build.isdigit():
            raise TypeError("Builds can only be deleted with their identifiers")
        if self.get_build_owner(build) != owner:
            raise PermissionError("Shame on you. You are not the owner of that build.")
        name = self.get_build_name(build, owner)
        self.exec_command(delete.DELETE_BUILD_BY_ID.format(build=build))
        return name

    def insert_strategy(self, owner: str, strategy: Strategy):
        """Insert a Strategy into the database"""
        name, data = strategy.name, strategy.serialize()
        command = insert.INSERT_STRATEGY.format(owner=owner, name=name)
        return self.exec_command(command, (data,))

    def get_strategies(self, owner: str):
        """Return all strategies owned by a certain client"""
        query = select.GET_STRATEGIES.format(owner=owner)
        r = self.exec_query(query)
        if len(r) == 0:
            return None
        return r

    def get_strategy_data(self, owner: str, name: str):
        """Return the serialized strategy data"""
        query = select.GET_STRATEGY_DATA.format(owner=owner, name=name)
        r = self.exec_query(query)
        if len(r) == 0:
            return None
        return r[0]

    def delete_strategy(self, owner, name):
        """Delete a strategy given a strategy name and owner"""
        command = delete.DELETE_STRATEGY.format(owner=owner, name=name)
        return self.exec_command(command)
