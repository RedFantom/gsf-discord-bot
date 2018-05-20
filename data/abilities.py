"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

primary = {
    "hlc": "Heavy Laser Cannon",
    "lc": "Laser Cannon",
    "llc": "Light Laser Cannon",
    "qlc": "Quad Laser Cannon",
    "rfl": "Rapid-fire Laser Cannon",
    "ic": "Ion Cannon",
    "blc": "Burst Laser Cannon"
}

secondary = {
    "protons": "Proton Torpedo",
    "concussions": "Concussion Missile",
    "thermites": "Thermite Torpedo",
    "clusters": "Cluster Missiles",
    "seekers": "Seeker Mines",
    "pods": "Rocket Pods",
    "empm": "EMP Missile",
    "ionm": "Ion Missile",
    "probes": "Sabotage Probe",
    "seismics": "Seismic Mines",
    "slug": "Slug Railgun",
    "ion": "Ion Railgun",
    "plasma": "Plasma Railgun",
    "interdiction": "Interdiction Missile",
}

engine = {
    "spc": "Shield Power Converter",
    "wpc": "Weapon Power Converter",
    "epc": "Engine Power Converter",
    "rotationals": "Rotational Thrusters",
    "kturn": "Koiogran Turn",
    "koiogran": "Koiogran Turn",
    "sturn": "Snap Turn",
    "snap": "Snap Turn",
    "retros": "Retro Thrusters",
    "pd": "Power Dive",
    "dive": "Power Dive",
    "interdiction": "Interdiction Drive",
    "beacon": "Hyperspace Beacon",
    "barrel": "Barrel Roll",
    "roll": "Barrel Roll"
}

systems = {
    "rsd": "Railgun Sentry Drone",
    "isd": "Interdiction Sentry Drone",
    "msd": "Missile Sentry Drone",
    "tt": "Targeting Telemetry",
    "telemetry": "Targeting Telemetry",
    "bo": "Blaster Overcharge",
    "blaster": "Blaster Overcharge",
    "booster": "Booster Overcharge",
    "cc": "Combat Command",
    "combat": "Combat Command",
    "command": "Combat Command",
    "rp": "Repair Probes",
    "repair": "Repair Probes",
    "probes": "Repair Probes",
    "rs": "Remote Slicing",
    "remote": "Remote Slicing",
    "slicing": "Remote Slicing",
    "sb": "Sensor Beacon",
    "beacon": "Sensor Beacon",
    "sensors": "Sensor Beacon",
    "empf": "EMP Field",
    "interdictions": "Interdiction Mine",
    "ions": "Ion Mine",
    "concs": "Concussion Mine",
    "concussions": "Concussion Mine",
    "tf": "Tensor Field",
    "tensor": "Tensor Field"
}

shields = {
    "cp": "Charged Plating",
    "sp": "Shield Projector",
    "projector": "Shield Projector",
    "repair": "Repair Drone",
    "rp": "Repair Drone",
    "drone": "Repair Drone",
    "fortress": "Fortress Shield",
    "feedback": "Feedback Shield",
    "directionals": "Directional Shield",
    "ds": "Directional Shield",
    "df": "Distortion Field",
    "distortion": "Distortion Field",
    "qcs": "Quick-Charge Shield",
    "quick-charge": "Quick-Charge Shield"
}

reactor = {
    "large": "Large Reactor",
    "turbo": "Turbo Reactor",
    "regen": "Regeneration Reactor",
}

magazine = {
    "munitions": "Munitions Capacity Extender",
    "power": "Power Pool Extender",
    "regen": "Regeneration Extender",
}

armor = {
    "evasion": "Lightweight Armor",
    "dr": "Deflection Armor",
    "hull": "Reinforced Armor",
    "targeting": "Efficient Targeting",
}

sensors = {
    "damps": "Dampening Sensors",
    "range": "Range Sensors",
    "comms": "Communication Sensors"
}

capacitor = {
    "frequency": "Frequency Capacitor",
    "damage": "Damage Capacitor",
    "range": "Range Capacitor",
}

thrusters = {
    "regen": "Regeneration Thrusters",
    "power": "Power Thrusters",
    "speed": "Speed Thrusters",
    "turning": "Turning Thrusters",
}

majors = ["primary", "primary2", "secondary", "secondary2", "systems"]
middle = ["engine", "shields"]
minors = ["reactor", "magazine", "thrusters", "sensors", "capacitor", "armor"]

upgrades = {
    "major": [0, 1, 2, (3, 0), (3, 1), (4, 0), (4, 1)],
    "middle": [0, 1, (2, 0), (2, 1)],
    "minor": [0, 1, 2]
}
