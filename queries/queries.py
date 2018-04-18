"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

INSERT_USER = """
    INSERT INTO User(id) VALUES ('{}')
"""

UPDATE_HOME = """
    UPDATE User SET home = '{1}' WHERE id = '{0}'
"""  #.format(discord_id, home)


