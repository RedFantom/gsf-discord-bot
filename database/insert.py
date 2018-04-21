"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

INSERT_USER = """
    INSERT INTO User(id, code) VALUES ('{discord}', '{code}');
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
    INSERT INTO Character(name, server, faction, owner) VALUES 
        ('{name}', '{server}', '{faction}', '{owner}');
"""

INSERT_MATCH = """
    INSERT INTO Match(server, start) values 
        ('{server}', '{start}');
"""

UPDATE_MATCH_SCORE = """
    UPDATE 'Match' SET score = '{score}' WHERE start = '{start}' AND server = '{server}'; 
"""

UPDATE_MATCH_END = """
    UPDATE 'Match' SET 'end' = '{end}' WHERE start = '{start}' AND server = '{server}';
"""

UPDATE_MATCH_MAP = """
    UPDATE 'Match' SET 'map' = '{map}' WHERE start = '{start}' AND server = '{server}';
"""

INSERT_RESULT = """
    INSERT INTO Result('match', char, assists, damage, deaths) VALUES 
        ({match}, {char}, {assists}, {damage}, {deaths});
"""
