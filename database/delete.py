"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""


DELETE_RESULTS_CHARACTER = "DELETE FROM Result WHERE char = {char_id};"
DELETE_CHARACTERS = "DELETE FROM 'Character' WHERE owner = '{discord_id}';"
DELETE_USER = "DELETE FROM 'User' WHERE id = '{discord_id}';"
DELETE_BUILD_BY_ID = "DELETE FROM 'Builds' WHERE build = {build};"
DELETE_STRATEGY = "DELETE FROM 'Strategies' WHERE owner = '{owner}' AND name = '{name}';"
