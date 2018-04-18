"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

CREATE_TABLE_SERVER = """
    CREATE TABLE IF NOT EXISTS Server(
        id TEXT PRIMARY KEY,
        name TEXT,
        region TEXT
    );
"""


CREATE_TABLE_USER = """
    CREATE TABLE IF NOT EXISTS User(
        id TEXT PRIMARY KEY,
        home TEXT REFERENCES Server.id
    );
"""

CREATE_TABLE_CHARACTER = """
    CREATE TABLE IF NOT EXISTS Character(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        server TEXT REFERENCES Server.id NOT NULL,
        faction TEXT NOT NULL,
        owner INTEGER REFERENCES User.id NOT NULL
    );
"""

CREATE_TABLE_MATCH = """
    CREATE TABLE IF NOT EXISTS 'Match'(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server TEXT REFERENCES Server.id NOT NULL,
        time TEXT,
        score TEXT
    );
"""

CREATE_TABLE_RESULT = """
    CREATE TABLE IF NOT EXISTS Match(
        match INTEGER REFERENCES Match.id,
        char INTEGER REFERENCES Character.id,
        assists INTEGER,
        damage INTEGER,
        deaths INTEGER,
        PRIMARY KEY(match, char)
    );
"""
