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

GET_USER_ID = "SELECT id FROM User WHERE id = '{discord_id}';"

GET_USER_LAST = "SELECT last FROM User WHERE id = '{discord}';"

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
    SELECT name, faction, dmgd, dmgt, assists, deaths, ship
    FROM Character
        INNER JOIN Result ON 'Character'.id = 'Result'.char
        INNER JOIN 'Match' ON 'Match'.id = 'Result'.match 
    WHERE Match.date = '{date}' AND Match.server = '{server}' AND Match.start = '{start}';
"""

GET_BUILD_BY_NAME = """
    SELECT build, public FROM Builds WHERE name = '{name}' AND owner = '{owner}';
"""

GET_BUILD_BY_ID = """
    SELECT build, public FROM Builds WHERE build = {build};
"""

GET_BUILD_OWNER = """
    SELECT owner FROM Builds WHERE build = {build};
"""

GET_BUILD_PUBLIC = """
    SELECT public FROM Builds WHERE build = {build};
"""

GET_BUILDS_BY_OWNER = """
    SELECT build, name, data, public FROM Builds WHERE owner = '{owner}';
"""

GET_BUILDS_PUBLIC = """
    SELECT build, name, data FROM Builds WHERE public = 1;
"""

GET_BUILD_DATA = """
    SELECT data FROM Builds WHERE build = {build};
"""

GET_BUILD_NAME = """
    SELECT name FROM Builds WHERE build = {build};
"""

GET_BUILD_PUBLIC = """
    SELECT public FROM Builds WHERE build = {build};
"""

GET_STRATEGY_DATA = """
    SELECT data FROM Stategies WHERE owner = '{owner}' AND name = '{name}';
"""

GET_STRATEGIES = """
    SELECT name FROM Strategies WHERE owner = '{owner}';
"""
