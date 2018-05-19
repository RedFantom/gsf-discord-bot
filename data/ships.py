"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""

ship_categories = [
    "Strike Fighter",
    "Scout",
    "Gunship",
    "Bomber",
]

ship_tier_letters = ["F", "S", "G", "B"]

ship_tiers = {
    # Scouts
    "Blackbolt": "T1S",
    "Novadive": "T1S",
    "Sting": "T2S",
    "Flashfire": "T2S",
    "Bloodmark": "T3S",
    "Spearpoint": "T3S",
    # Bombers
    "Razorwire": "T1B",
    "Rampart Mark Four": "T1B",
    "Legion": "T2B",
    "Warcarrier": "T2B",
    "Decimus": "T3B",
    "Sledgehammer": "T3B",
    # Gunships
    "Mangler": "T1G",
    "Quarrel": "T1G",
    "Dustmaker": "T2G",
    "Comet Breaker": "T2G",
    "Jurgoran": "T3G",
    "Condor": "T3G",
    # Strike Fighters
    "Rycer": "T1F",
    "Star Guard": "T1F",
    "Quell": "T2F",
    "Pike": "T2F",
    "Imperium": "T3F",
    "Clarion": "T3F"
}

ship_tier_factions = {
    "I1S": "Blackbolt",
    "I2S": "Sting",
    "I3S": "Bloodmark",
    "I1F": "Rycer",
    "I2F": "Quell",
    "I3F": "Imperium",
    "I1B": "Razorwire",
    "I2B": "Legion",
    "I3B": "Decimus",
    "I1G": "Mangler",
    "I2G": "Dustmaker",
    "I3G": "Jurgoran",
    "R1S": "Novadive",
    "R2S": "Flashfire",
    "R3S": "Spearpoint",
    "R1F": "Star Guard",
    "R2F": "Pike",
    "R3F": "Clarion",
    "R1B": "Rampart Mark Four",
    "R2B": "Warcarrier",
    "R3B": "Sledgehammer",
    "R1G": "Quarrel",
    "R2G": "Comet Breaker",
    "R3G": "Condor",
}

ship_names = {
    "Decimus": "Imperial_B-5_Decimus",
    "Quell": "Imperial_F-T2_Quell",
    "Imperium": "Imperial_FT-3C_Imperium",
    "Rycer": "Imperial_F-T6_Rycer",
    "Mangler": "Imperial_GSS-3_Mangler",
    "Jurgoran": "Imperial_GSS-4Y_Jurgoran",
    "Dustmaker": "Imperial_GSS-5C_Dustmaker",
    "Onslaught": "Imperial_G-X1_Onslaught",
    "Frostburn": "Imperial_ICA-2B_Frostburn",
    "Sable Claw": "Imperial_ICA-3A_-_Sable_Claw",
    "Tormentor": "Imperial_ICA-X_Tormentor",
    "Ocula": "Imperial_IL-5_Ocula",
    "Demolisher": "Imperial_K-52_Demolisher",
    "Razorwire": "Imperial_M-7_Razorwire",
    "Blackbolt": "Imperial_S-12_Blackbolt",
    "Sting": "Imperial_S-13_Sting",
    "Bloodmark": "Imperial_S-SC4_Bloodmark",
    "Gladiator": "Imperial_TZ-24_Gladiator",
    "Mailoc": "Imperial_VX-9_Mailoc",
    "Banshee": "Republic_Banshee",
    "Flashfire": "Republic_Flashfire",
    "Pike": "Republic_FT-6_Pike",
    "Clarion": "Republic_FT-7B_Clarion",
    "Star Guard": "Republic_FT-8_Star_Guard",
    "Firehauler": "Republic_G-X1_Firehauler",
    "Skybolt": "Republic_IL-5_Skybolt",
    "Strongarm": "Republic_K-52_Strongarm",
    "Novadive": "Republic_NovaDive",
    "Rampart Mark Four": "Republic_Rampart_Mark_Four",
    "Comet Breaker": "Republic_SGS-41B_Comet_Breaker",
    "Quarrel": "Republic_SGS-45_Quarrel",
    "Condor": "Republic_SGS-S1_Condor",
    "Sledgehammer": "Republic_Sledgehammer",
    "Spearpoint": "Republic_Spearpoint",
    "Enforcer": "Republic_TZ-24_Enforcer",
    "Redeemer": "Republic_VX-9_Redeemer",
    "Warcarrier": "Republic_Warcarrier",
    "Whisper": 'Republic_X5-Whisper',
    "Mirage": "Republic_X7-Mirage",
    "Legion": "Imperial_B-4D_Legion"
}

ships_names_reverse = {value: key for key, value in ship_names.items()}
