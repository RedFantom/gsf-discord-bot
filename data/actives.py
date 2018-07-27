"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom
"""

ACTIVES = {
    "Bypass": {"Weapon_Shield_Piercing": 0.18},
    "Concentrated Fire": {"Crit_Chance": 0.36},
    "Hydro Spanner": {"Max_Health": 308},
    "Lingering Effect": None,
    "Lockdown": None,
    "Nullify": {"Ship_Damage_Reduction": 0.30},
    "Running Interference": {"Ship_Evasion": 0.15},
    "Servo Jammer": {
        "[Pc]Engine_Base_Speed": -0.20,
        "[Pc]Turn_Rate_Modifier": -0.20},
    "Slicer's Loop": {
        "[Pc]Power_Engine_Regen_Rate": -1.0,
        "[Pc]Power_Shield_Regen_Rate": -1.0,
        "[Pc]Power_Weapon_Regen_Rate": -1.0},
    "Suppression": {"Weapon_Base_Accuracy": -0.20},
    "Wingman": {"Weapon_Base_Accuracy": 0.20},
    "Blaster Overcharge": {
        "[Pc]Weapon_Rate_of_Fire": 0.25,
        "[Pc]Power_Weapon_Regen_Rate": 0.15,
        "TalentTree": {
            (0, 0): {},
            (1, 0): {"Crit_Chance": 0.08},
            (2, 0): {},
            (3, 0): {"Power_Weapon_Regen_Rate": 0.14, "Target": "self"},
            (3, 1): {"Weapon_Rate_of_Fire": 0.08, "Target": "self"},
            (4, 0): {"[Pc]Weapon_Base_Damage": 0.10, "Target": "PrimaryWeapons"},
            (4, 1): {
                "[Pc]Weapon_Range_Long": 0.10,
                "[Pc]Weapon_Range_Mid": 0.10,
                "[Pc]Weapon_Range_Pb": 0.10,
                "Target": "PrimaryWeapons"},
        }}
}
