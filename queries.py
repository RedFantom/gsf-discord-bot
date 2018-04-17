"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

"""
Database Model

    Server
    id - Server three-letter code - TEXT PRIMARY KEY
    name - Common server name - TEXT
    region - Three-letter region code (USA/EUR) - TEXT

    Character
    id - Character ID - INTEGER PRIMARY KEY
    name - Character name - TEXT
    server - Server three-letter code - TEXT
    faction - Faction three-letter code - TEXT
    owner - User ID - REFERENCES User.id
    
    User
    id - Unique Discord User ID - TEXT PRIMARY KEY
    home - Server three-letter code - TEXT
    
    Match
    id - Match ID - INTEGER PRIMARY KEY
    server - Server three-letter code - TEXT
    time - Timestamp of match start - TEXT
    score - Result score ("{empire}-{republic}") - TEXT
    
    Result
    match - Match ID - INTEGER REFERENCES Match.id
    char - Character ID - INTEGER REFERENCES Character.id
    assists - Number of assists - INTEGER
    damage - Amount of damage dealt - INTEGER
    deaths - Amount of deaths - INTEGER
    PRIMARY KEY: (match, char)
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
