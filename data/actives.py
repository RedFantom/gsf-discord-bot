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
        }},
    "Booster Recharge": {
        "TalentTree": {
            (0, 0): {}, (1, 0): {}, (2, 0): {},
            (3, 0): {"[Pc]Power_Engine_Regen_Rate": 0.10},
            (3, 1): {"[Pc]Engines_Max_Power": 0.10},
            (4, 0): {}, (4, 1): {}
        }},
    "Charged Plating": {
        "Ship_Damage_Reduction": 0.60,
        "TalentTree": {
            (0, 0): {"[Pc]Shield_Bleed_Through": -0.10},
            (1, 0): {}, (2, 0): {}, (2, 1): {}
        }},
    "Combat Command": {
        "Weapon_Base_Accuracy": 0.10,
        "TalentTree": {
            (0, 0): {}, (1, 0): {}, (2, 0): {},
            (3, 0): {"[Pc]Weapon_Max_Power": 0.10},
            (3, 1): {"Crit_Chance": 0.07, "Target": "PrimaryWeapons"},
            (4, 0): {},
            (4, 1): {"Weapon_Base_Accuracy": 0.10, "Target": "PrimaryWeapons"}
        }},
    "Directional Shield": {},
    "Distortion Field": {
        "Ship_Evasion": 0.27,
        "TalentTree": {
            (0, 0): {"Ship_Evasion": 0.08},
            (1, 0): {}, (2, 0): {}, (2, 1): {}
        }},
    "Fortress Shield": {
        "[Pc]Shields_Max_Power_(Capacity)": 1.30,
        "Sensor_Dampening": 15,
        "Engine_Speed_Multiplier": -1.0,
        "TalentTree": {
            (0, 0): {},
            (1, 0): {
                "[Pc]Shields_Max_Power_(Capacity)": 0.20,
                "Target": "self"},
            (2, 0): {},
            (2, 1): {"[Pc]Power_Weapon_Regen_Rate": 0.30}
        }},
    "Interdiction Driver": {
        "Engine_Speed_Multiplier": 0.50,
        "TalentTree": {
            (0, 0): {},
            (1, 0): {"Engine_Speed_Multiplier": 0.10},
            (2, 0): {}, (2, 1): {},
        }},
    "Koiogran Turn": {
        "Ship_Evasion": 0.24,
        "Weapon_Base_Accuracy": 0.50,
        "TalentTree": {
            (0, 0): {}, (1, 0): {},
            (2, 0): {"Engine_Speed_Multiplier": 0.10},
            (2, 1): {"Turn_Rate_Modifier": 0.10},
        }},
    "Overcharged Shield": {
        "[Pc]Shields_Max_Power_(Capacity)": 0.18,
        "TalentTree": {
            (0, 0): {}, (1, 0): {}, (2, 0): {},
            (2, 1): {
                "[Pc]Shields_Max_Power_(Capacity)": 0.09,
                "Target": "self"
            }
        }},
    "Power Dive": {
        "Ship_Evasion": 0.24,
        "TalentTree": {
            (0, 0): {}, (1, 0): {},
            (2, 0): {"Engine_Speed_Multiplier": 0.10},
            (2, 1): {"Turn_Rate_Modifier": 0.10}
        }},
}
