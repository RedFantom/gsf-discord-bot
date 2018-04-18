# Database Model

### Server
```sqlite
id - Server three-letter code - TEXT PRIMARY KEY
name - Common server name - TEXT
region - Three-letter region code (USA/EUR) - TEXT
```

### Character
```sqlite
id - Character ID - INTEGER PRIMARY KEY
name - Character name - TEXT
server - Server three-letter code - TEXT
faction - Faction three-letter code - TEXT
owner - User ID - REFERENCES User.id
```

### User
```sqlite
id - Unique Discord User ID - TEXT PRIMARY KEY
home - Server three-letter code - TEXT
```

### Match
```sqlite
id - Match ID - INTEGER PRIMARY KEY
server - Server three-letter code - TEXT
time - Timestamp of match start - TEXT
score - Result score ("{empire}-{republic}") - TEXT
```

### Result
```sqlite
match - Match ID - INTEGER REFERENCES Match.id
char - Character ID - INTEGER REFERENCES Character.id
assists - Number of assists - INTEGER
damage - Amount of damage dealt - INTEGER
deaths - Amount of deaths - INTEGER
PRIMARY KEY: (match, char)
```
