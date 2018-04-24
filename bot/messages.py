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

INVALID_ARGS = "Those are not valid arguments for that command."
INVALID_DATE_RANGE = "That is not a valid date range."
INVALID_SERVER = "That is not a valid server name. Please use a server abbreviation."

UNREGISTER = "I have deleted all of your data from the database."
UNREGISTER_PUBLIC = "{}, you are now no longer registered."
UNKNOWN_CHARACTER = "The character `{}` on `{}` is not in my database."
UNKNOWN_DATE_FORMAT = "I do not recognize that date format. Please use YYYY-MM-DD."
UNKNOWN_TIME_FORMAT = "I do not recognize that time format. Please use HH:MM instead."

CHARACTER_OWNER = "`{}` owns that character."

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

# Data retrieval
'day {date}': List the amount of matches registered on each server for 
    a given date. If the date is omitted, I will assume you mean today. 
'week': List the amount of matches registered on each server for the 
    last seven days.
'period {start} {end}': List the amount of matches registered on each
    server for a specified period. If the 'end' argument is not given,
    I will assume you mean today.
'matches {server} {date}': List the matches registered for a given
    server and date. Lists at least the start time and, if available,
    also the end time, match type, map type, end score and winning 
    faction. If the 'date' argument is omitted, I will assume you mean
    today.
'character {server} {name}': Find the owner of the character specified
    by the server and name. Note that the matching is sensitive for 
    capital and accented letters.

# Data insertion
'match {start} {end} {type} {map} {score}': Not yet implemented. 
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

MATCH_COUNT_DAY = """
On {}, I registered the following amount of matches on each server:
```python
{}
```
"""

MATCH_COUNT_PERIOD = """
From {} to {}, I registered the following amount of matches on each server:
```python
{}
```
"""

MATCH_COUNT_WEEK = """
During the last week, I registered the following amount of matches on each server:
```python
{}
```
"""

NOT_IMPLEMENTED = "Sorry, that feature has not yet been implemented. " \
                  "Poke RedFantom if you would like to see it sooner."

MATCH_OVERVIEW = """
On {} I registered the following matches on `{}`:
```python
 start |  end  |   type   |   map   
------------------------------------
{}
```
"""
# 00:00   00:00    DOM      KM     1000-456  Empire

NO_MATCHES_FOUND = "I could not find any matches for the specified criteria."

RESULTS = """
For the match starting at `{}` on `{}` on server `{}`, the following results were sent:
```python
      Name      |  Faction  | DMG Dealt | DMG Taken | Enemies hit | Deaths 
---------------------------------------------------------------------------
{}
"""

NO_RESULTS = """I don't have any results for that match in my database."""
