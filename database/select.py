"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

GET_CHARACTER_ID = """
    SELECT id FROM 'Character' WHERE name = '{name}' AND server = '{server}';
"""

GET_MATCH_ID = """
    SELECT id FROM 'Match' 
    WHERE 
      server = '{server}' AND
      date = '{date}' AND
      idfmt = '{idfmt}';
"""

GET_AUTH_CODE = """
    SELECT code FROM 'User' WHERE id = '{discord}';
"""

GET_CHARACTER_IDS = """
    SELECT id FROM 'Character' WHERE owner = '{discord_id}';
"""

GET_USER_ID = "SELECT id FROM 'User' WHERE id = '{discord_id}';"

GET_CHARACTER_OWNER = """
    SELECT 'User'.id FROM 'User', 'Character' 
    WHERE  'Character'.name = '{name}' AND 'Character'.server = '{server}';
"""

GET_MATCHES_COUNT_FOR_DAY_BY_SERVER = """
    SELECT server, COUNT(id) FROM Match
    WHERE date = '{date}' GROUP BY server;
"""

GET_MATCHES_FOR_DAY_FOR_SERVER = """
    SELECT start, end, map, score FROM Match
    WHERE server = '{server}' AND date = '{date}';
"""

GET_MATCH_RESULTS = """
    SELECT name, faction, dmgd, dmgt, damage, deaths
    FROM Character
        INNER JOIN Result ON 'Character'.id = 'Result'.char
        INNER JOIN 'Match' ON 'Match'.id = 'Result'.match 
    WHERE Match.date = '{date}' AND Match.server = '{server}' AND Match.start = '{start}';
"""
