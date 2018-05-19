"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

component_types = {
    "primary": "PrimaryWeapon",
    "primary2": "PrimaryWeapon2",
    "secondary": "SecondaryWeapon",
    "secondary2": "SecondaryWeapon2",
    "engine": "Engine",
    "shields": "ShieldProjector",
    "systems": "Systems",
    "armor": "Armor",
    "reactor": "Reactor",
    "magazine": "Magazine",
    "sensors": "Sensor",
    "thrusters": "Thruster",
    "capacitor": "Capacitor"
}

component_types_reverse = {value: key for key, value in component_types.items()}

component_strings = {
    "PrimaryWeapon": "Primary Weapon",
    "PrimaryWeapon2": "Primary Weapon II",
    "SecondaryWeapon": "Secondary Weapon",
    "SecondaryWeapon2": "Secondary Weapon II",
    "ShieldProjector": "Shields",
    "Engine": "Engine",
    "Systems": "Systems",
    "Armor": "Armor",
    "Reactor": "Reactor",
    "Magazine": "Magazine",
    "Sensor": "Sensors",
    "Thruster": "Thrusters",
    "Capacitor": "Capacitor"
}

components = [
    "PrimaryWeapon",
    "PrimaryWeapon2",
    "SecondaryWeapon",
    "SecondaryWeapon2",
    "Engine",
    "ShieldProjector",
    "Systems",
    "Armor",
    "Reactor",
    "Magazine",
    "Sensor",
    "Thruster",
    "Capacitor"
]

component_short_hand = {
    "pw": "PrimaryWeapon",
    "p2": "PrimaryWeapon2",
    "sw": "SecondaryWeapon",
    "s2": "SecondaryWeapon2",
    "en": "Engine",
    "sp": "ShieldProjector",
    "sy": "Systems",
    "a": "Armor",
    "r": "Reactor",
    "m": "Magazine",
    "s": "Sensor",
    "t": "Thruster",
    "c": "Capacitor",
}

ship_key_to_shorthand = {
    "primary": "pw",
    "primary2": "p2",
    "secondary": "sw",
    "secondary2": "s2",
    "engine": "en",
    "shields": "sp",
    "systems": "sy",
    "armor": "a",
    "reactor": "r",
    "magazine": "m",
    "sensors": "s",
    "thrusters": "t",
    "capacitor": "c"
}

shorthand_to_ship_key = {value: key for key, value in ship_key_to_shorthand.items()}
