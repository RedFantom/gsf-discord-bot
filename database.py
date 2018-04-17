"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
from queue import Queue
from threading import Thread, Lock
import sqlite3 as sql
from queries import *
import logging


class DatabaseHandler(Thread):
    """
    Thread-safe database handler to allow the processing of queries
    of multiple clients. Uses Queues to allow thread-safe access and
    then executes the commands/queries one by one.
    """
    def __init__(self, file_name="database.db", log_level=logging.WARNING):
        """
        :param file_name: File name for the SQLite database
        :param log_level: Logger logging level
        """
        Thread.__init__(self)
        # Initialize database connection
        self.db = sql.connect(file_name)
        # Build logger
        logging.basicConfig(filename="database.log", level=log_level)
        logging.debug("Log file opened.")
        # Initialize the database
        self.init_db()

    def init_db(self):
        pass

    def create_tables(self):
        pass
