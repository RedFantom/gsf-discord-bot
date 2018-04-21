"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

GET_CHARACTER_ID = """
    SELECT id FROM 'Character' WHERE name = '{name}' AND server = '{server}';
"""

GET_MATCH_ID = """
    SELECT id FROM 'Match' WHERE start = '{start}' AND server = '{server}';
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
