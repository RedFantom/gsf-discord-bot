"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

INSERT_USER = """
    INSERT INTO User(id, code, last) VALUES ('{discord}', '{code}', '{last}');
"""

UPDATE_CODE = """
    UPDATE User SET code = '{code}' WHERE id = '{discord}';
"""

UPDATE_HOME = """
    UPDATE User SET home = '{discord}' WHERE id = '{home}';
"""

INSERT_SERVERS = """
    INSERT OR IGNORE INTO Server(id, name, region) VALUES 
        ('SA', 'Satele Shan', 'NA'),
        ('SF', 'Star Forge', 'NA'),
        ('TH', 'Tulak Hord', 'EU'),
        ('DM', 'Darth Malgus', 'EU'),
        ('TL', 'The Leviathan', 'EU');
"""

INSERT_CHARACTER = """
    INSERT OR IGNORE INTO Character(name, server, faction, owner) VALUES 
        ('{name}', '{server}', '{faction}', '{owner}');
"""

INSERT_MATCH = """
    INSERT OR IGNORE INTO 'Match'('server', 'date', 'start', 'idfmt') values 
        ('{server}', '{date}', '{start}', '{idfmt}');
"""

UPDATE_MATCH_SCORE = """
    UPDATE Match SET score = {score} WHERE id = {match}; 
"""

UPDATE_MATCH_END = """
    UPDATE Match SET end = '{end}' WHERE id = {match};
"""

UPDATE_MATCH_MAP = """
    UPDATE Match SET map = '{map}' WHERE id = {match};
"""

INSERT_RESULT = """
    INSERT OR IGNORE INTO Result(match, char, assists, dmgd, dmgt, deaths, ship) VALUES 
        ({match}, {char}, {assists}, {dmgd}, {dmgt}, {deaths}, '{ship}');
"""

INSERT_BUILD = """
    INSERT OR IGNORE INTO Builds(owner, name, data, public) VALUES
        ('{owner}', '{name}', '{data}', {public});
"""

UPDATE_BUILD_DATA = """
    UPDATE Builds SET data = '{data}' WHERE build = {build};
"""

UPDATE_BUILD_PUBLIC = """
    UPDATE Builds SET public = {public} WHERE build = {build};
"""

UPDATE_USER_LAST = """
    UPDATE User SET last = '{date}' WHERE id = '{tag}'
"""

INSERT_STRATEGY = """
    INSERT OR REPLACE INTO Strategies(owner, name, data) VALUES ('{owner}', '{name}', ?);
"""
