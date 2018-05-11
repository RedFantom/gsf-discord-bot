# GSF Discord Bot
[![Build Status](https://travis-ci.com/RedFantom/gsf-discord-bot.svg?token=UBcv5ZyxSrELyQhSpadq&branch=master)](https://travis-ci.com/RedFantom/gsf-discord-bot)

This Discord Bot is intended for use in Discord servers in use by the
SWTOR:GSF Community. This bot works in conjunction with the 
[GSF Parser](https://www.github.com/RedFantom/gsf-parser).

This Bot is free software, you can redistribute the code under GNU
GPLv3, but I would appreciate if you would not run a copy of this Bot
as intended for the GSF Community without letting me know.

The code is available mostly as a learning resource. You can use it to
see how `discord.py` can be used to build a Discord Bot.

### Set-up
The bot can easily be setup by cloning the repository into a folder
on a Linux machine, allowing full access to this folder to only a 
separate non-root user for security concerns, and then by creating a 
`systemd`-service file to allow running `main.py` continuously.
Of course, in addition a valid Discord Bot secure key must be provided
in `./discord`. The database will be created in `./database.db`.

### Usage
Once the bot is set-up, a set of commands is available through the use
of the selected command prefix. For a full list and manual of these
commands, please consult the `man` command.

### License

    GSF Parser Discord Bot and Server
    Copyright (C) 2018 RedFantom
    
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
