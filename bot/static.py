"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

AUTHOR_EMBED = (
    "Author and copyright information",
    "Thank the maker! Someone reading my copyright information.\n\n"
    "Copyright (c) 2018 RedFantom"
)

CONTENT_LICENSE = (
    "Content License",
    "Any and all content produced by this Discord Bot, is copyrighted "
    "by RedFantom and licensed under:\n\n"
    "*Creative Commons - Attribution-NonCommercial-ShareAlike 4.0*\n"
    "Read the whole license [here](https://creativecommons.org/licenses/by-nc-sa/4.0)."
)

CODE_LICENSE = (
    "Code License",
    "This program is free software: you can redistribute it and/or "
    "modify it under the terms of the GNU General Public License as "
    "published by the Free Software Foundation, version 3 of the "
    "License.\n\n"
    "This program is distributed in the hope that it will be useful, "
    "but WITHOUT ANY WARRANTY; without even the implied warranty of"
    "MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the "
    "GNU General Publice License for more details.\n\n"
    "You should have received a copy of the GNU General Public License "
    "along with this program. If not, see [gnu.org/licenses](http://www.gnu.org/licenses)."
)


PURPOSE = """
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
"""

PRIVACY = """
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
"""

SETUP = """
Setting up the GSF Parser to work with this bot is really easy. It can
be done in a few simple steps.

1. Download and install the latest version of the GSF Parser from
   <https://www.github.com/RedFantom/gsf-parser/releases>
2. Register yourself into my database with the `register` command.
3. Open the GSF Parser and let it initialize for the first time. This 
   may take a while.
4. You should have received a security code over PM. Enter this code,
   along with your Discord tag in `@Name#1234` format into the settings
   tab of the GSF Parser. It is saved automatically.
5. Go to the characters tab and enable Discord sharing for each
   character you want to share data of. If selected, match results 
   will be available through the `results` command and your Discord tag
   will be available through the `character` command.
6. Restart the GSF Parser to resynchronize with the Discord Bot Server,
   sharing the results for the characters you have selected.
"""

HELP = """
Hello! 

I am the GSF Parser Discord bot. Using the GSF Parser, you can send data
to me, that I use to provide interesting information to you. 

Use the `setup` command to get started.
Use the `link` command to get a GSF Parser download link.
Use the `purpose` command to find out more about why I am here.

Use the `man` command to find out more about the specific commands.
"""

EMBED_FOOTER = "Copyright (c) 2018 RedFantom, CC BY-NC-SA 4.0"
