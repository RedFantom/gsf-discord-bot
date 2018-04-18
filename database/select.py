"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

GET_CHARACTER_ID = """
    SELECT id FROM Character WHERE name = '{name}' AND server = '{server}';
"""

GET_MATCH_ID = """
    SELECT id FROM Match WHERE start = '{start}' AND server = '{server}';
"""

GET_AUTH_CODE = """
    SELECT code FROM User WHERE id = '{discord}';
"""
