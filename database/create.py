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
        home TEXT REFERENCES Server(id),
        code TEXT NOT NULL 
    );
"""

CREATE_TABLE_CHARACTER = """
    CREATE TABLE IF NOT EXISTS Character(
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        server TEXT REFERENCES Server(id) NOT NULL,
        faction TEXT NOT NULL,
        owner INTEGER REFERENCES User(id) NOT NULL,
        UNIQUE(name, server)
    );
"""

CREATE_TABLE_MATCH = """
    CREATE TABLE IF NOT EXISTS 'Match'(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server TEXT REFERENCES Server(id) NOT NULL,
        idfmt TEXT NOT NULL,
        date TEXT NOT NULL,
        start TEXT NOT NULL,
        end TEXT,
        score TEXT,
        map TEXT,
        UNIQUE (server, date, idfmt)
    );
"""

CREATE_TABLE_RESULT = """
    CREATE TABLE IF NOT EXISTS 'Result'(
        match INTEGER REFERENCES Match(id),
        char INTEGER REFERENCES Character(id),
        assists INTEGER NOT NULL,
        dmgd INTEGER NOT NULL,
        dmgt INTEGER NOT NULL,
        deaths INTEGER NOT NULL,
        ship TEXT NOT NULL,
        PRIMARY KEY(match, char)
    );
"""
