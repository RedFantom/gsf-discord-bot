"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

COMPONENT_TYPES = {
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

COMP_TYPES_REVERSE = {value: key for key, value in COMPONENT_TYPES.items()}

COMPONENT_STR = {
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

COMPONENT_KEYS = [
    "primary",
    "primary2",
    "secondary",
    "secondary2",
    "shields",
    "engine",
    "systems",
    "armor",
    "reactor",
    "magazine",
    "sensors",
    "thrusters",
    "capacitor"
]

COMPONENTS = [
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

COMP_SHORT_HAND = {
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

SHIP_KEY_TO_SH = {
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

SH_TO_SHIP_KEY = {value: key for key, value in SHIP_KEY_TO_SH.items()}

WEAPON_CATEGORIES = [
    "PrimaryWeapon",
    "PrimaryWeapon2",
    "SecondaryWeapon",
    "SecondaryWeapon2"
]
