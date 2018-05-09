"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

UPON_REGISTER = "Welcome! Enter the following code in the GSF Parser to get " \
    "started: {}. Please note that by using this bot you agree to the " \
    "licensing terms as available through the `author` command."

UPON_REGISTER_PUBLIC = """You are now registered."""

ALREADY_REGISTERED = "You are already registered. Use the `forgot_code` " \
    "command to obtain a new access code."

NOT_REGISTERED = "You are not registered."

NEW_CODE = "Your new authentication code: {}. Your old code is now invalid."

INVALID_COMMAND = "That is either not a valid command or it does not have the " \
                  "correct arguments. Please check the `man` command."
NOT_PRIVATE = "Please don't PM me for any other purpose than the `forgot_code` or Bot Information commands."

INVALID_ARGS = "Those are not valid arguments for that command."
INVALID_DATE_RANGE = "That is not a valid date range."
INVALID_SERVER = "That is not a valid server name. Please use a server abbreviation."

UNREGISTER = "I have deleted all of your data from the database."
UNREGISTER_PUBLIC = "You are now no longer registered. All your data has been removed."
UNKNOWN_CHARACTER = "The character `{}` on `{}` is not in my database."
UNKNOWN_DATE_FORMAT = "I support many different date and time formats. For formats that consist of " \
                      "multiple elements (with spaces), please enclose them in quotes. If in doubt, " \
                      "use `YYYY-MM-DD` or `HH:MM`."
UNSUPPORTED_IMAGE_TYPE = "File `{}` has an unsupported file type for images."

CHARACTER_OWNER = "`{}` owns that character."

SERVER_STATUS = """
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

NOT_A_SCOREBOARD = "I do not recognize that image as a screenshot of a scoreboard.\n\n" \
                   "If it is a scoreboard, please send this message to the Maker " \
                   "to ask if support for this size and scale can be implemented. " \
                   "You must include this image, as well as your Global UI Scaling Factor."

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
 start |  end  |   type   |   map   |  score  |  winner  
---------------------------------------------------------
{}
```
"""
# 00:00   00:00    DOM      KM     1000-456  Empire

NO_MATCHES_FOUND = "I could not find any matches for the specified criteria."

RESULTS = """
For the match starting at `{}` on `{}` on server `{}`, the following results were sent:
```python
Name            | Faction   | DMG Dealt | DMG Taken | Enemies hit | Deaths | Ship Type     
---------------------------------------------------------------------------------------
{}
```
"""

NO_RESULTS = """I don't have any results for that match in my database."""

DOWNLOADING_IMAGES = "Downloading image: {}/{}"

SERVER_ONLINE = """`{}` just came online."""
SERVER_OFFLINE = """`{}` just went offline."""

GITHUB_RATE_LIMIT = "Sorry, the GitHub API rate limit has been exceeded. " \
    "Please try again later."

GITHUB_DOWNLOAD_LINK = \
    "The most recent version of the GSF Parser is `{}`.\n" \
    "```markdown\n" \
    "Setup: <{}>\n" \
    "Archive: <{}>\n" \
    "```"

MATCHES_TABLE = """
```markdown
# state |    server    | type | map                | score | Running for
-------------------------------------------------------------------------
{}
```
"""

MATCHES_ROW = " {:<6} | {:<13}| {:<4} | {:<18} | {:.2f}{} | {:02d}:{:02d} \n"
