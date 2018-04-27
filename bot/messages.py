"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

UPON_REGISTER = "Welcome! Enter the following code in the GSF Parser to get " \
    "started: {}"

UPON_REGISTER_PUBLIC = """You are now registered."""

ALREADY_REGISTERED = "You are already registered. Use the `forgot_code` " \
    "command to obtain a new access code."

NOT_REGISTERED = "You are not registered."

NEW_CODE = "Your new authentication code: {}. Your old code is now invalid."

INVALID_COMMAND = "That is either not a valid command or it does not have the " \
                  "correct arguments. Please check the `man` command."
NOT_PRIVATE = "Please don't PM me for any other purpose than the `forgot_code` or `man` commands."

INVALID_ARGS = "Those are not valid arguments for that command."
INVALID_DATE_RANGE = "That is not a valid date range."
INVALID_SERVER = "That is not a valid server name. Please use a server abbreviation."

UNREGISTER = "I have deleted all of your data from the database."
UNREGISTER_PUBLIC = "You are now no longer registered. All your data has been removed."
UNKNOWN_CHARACTER = "The character `{}` on `{}` is not in my database."
UNKNOWN_DATE_FORMAT = "I do not recognize that date format. Please use YYYY-MM-DD."
UNKNOWN_TIME_FORMAT = "I do not recognize that time format. Please use HH:MM instead."

CHARACTER_OWNER = "`{}` owns that character."

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
      Name      |  Faction  | DMG Dealt | DMG Taken | Enemies hit | Deaths |   Ship Type   
-------------------------------------------------------------------------------------------
{}
```
"""

NO_RESULTS = """I don't have any results for that match in my database."""

AUTHOR = """
Thank the Maker! Someone reading my copyright information.

Copyright (C) 2018 RedFantom

```markdown
# Content License

Any and all content produced by this Discord Bot, produced from 
information sent by GSF Parser users, is copyrighted by RedFantom
and licensed under:

Creative Commons - Attribution-NonCommercial-ShareAlike
For more information, check: 
<https://creativecommons.org/licenses/by-nc-sa/4.0/>
```

```markdown
# Code License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
"""

PURPOSE = """
```markdown
My primary programming consists of collecting data in order to allow 
users to interact socially with the statistics collected by the GSF
Parser. However, with the collection of this data, a few interesting
possibilities arise for the use of this data. Imagine answering 
questions like:
- What are the busiest parts of the day on each server? When are 
  relatively quiet periods during the year?
- Are matches on certain maps more often imbalanced than others?
- Do players choose different ships on different maps, and do different
  ships perform better or worse in particular maps?
- Are certain servers particularly bad when it comes to balance?
- Can the pop-rate on servers be calculated and, if so, can it be 
  predicted?
  
By uploading your data to my database, you will help my Maker answer 
these very questions! My code is open-source and available at GitHub.
Note though, that if you use parts of my code, you will have to use the
same license as my Maker used. Please use the `author` command to learn
more about the GNU GPLv3.
``` 
"""

PRIVACY = """
```markdown
My primary programming is allowing social interaction of users with 
statistical data, thus allowing free access to my database through a
given set of commands. While your data is saved on a VPS that is not
accessible from the outside world without a strong security (SSH) key, 
data mining through commands or other misuse of my services, in addition 
to hacks of the VPS might cause leaks of the data in the database. Data 
collected includes:
- Your Discord tag
- A SHA256 hash of your access key
- Your character data for the by you selected characters for sharing in
  the GSF Parser Characters menu (name, server, faction)
- Non-personal match data, including the server the match occurred on, 
  the start time, end time, map and end score of match.
- Personal match data, including number of enemies damaged, deaths, 
  damage dealt and damage taken, linked to a specific character and
  match.
```
"""
