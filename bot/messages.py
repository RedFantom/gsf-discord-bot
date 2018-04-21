"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

UPON_REGISTER = "Welcome! Enter the following code in the GSF Parser to get " \
    "started: {}"

UPON_REGISTER_PUBLIC = """{}, you are now registered."""

ALREADY_REGISTERED = "You are already registered. Use the `forgot_code` " \
    "command to obtain a new access code."

NOT_REGISTERED = "{}, you are not registered."

NEW_CODE = "Your new authentication code: {}. Your old code is now invalid."

INVALID_COMMAND = "{}, that is not a valid command. Please check the `manual` " \
                  "command."

UNREGISTER = "I have deleted all of your data from the database."
UNREGISTER_PUBLIC = "{}, you are now no longer registered."
UNKNOWN_CHARACTER = "The character `{}` on `{}` is not in my database."

CHARACTER_OWNER = "{} owns that character."

MANUAL = """
Hello! I am the GSF Parser-based Discord Bot. I am capable of 
tracking matches and player results based on data sent by GSF Parser
users. Using that data, I can compose different types of overviews.
Please check the list of commands below to get started. 

Commands: ```python
# Users
'register': Register yourself as a user into my database. I will send 
    you a unique access code to enter into the GSF Parser.
'unregister': Unregister yourself from the database. All your data will
    be removed if you issue this command, and this action is 
    irreversible.
'forgot_code': If you no longer have your unique access code, I can
    generate a new one for you. 

# Data
'overview': 
'characters':
```
"""

SERVERS = """
The following servers are in my database:
```markdown
# Region Europe
DM - Darth Malgus - {darth_malgus}
TH - Tulak Hord - {tulak_hord}
TL - The Leviathan - {the_leviathan}

# Region North-America
SF - Star Forge - {star_forge}
SA - Satele Shan - {satele_shan}
```
"""
