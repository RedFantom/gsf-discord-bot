"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""

categories = ["Hull_and_Shields", "Engine", "Maneuverability", "Weapons", "Sensors"]
weapon_categories = ["General", "Accuracy", "Range", "Missile", "Railgun"]
actives = ["Shields", "Engine"]

STATISTICS = {
    'Booster_Acceleration': ("Engine", "Boost Acceleration", "m/s^2"),
    'Booster_Activation_Power_Cost': ("Engine", "Boost Activation Power Cost", "p"),
    'Booster_Maneuverability_Modifier': ("Engine", "Boost Maneuverability Modifier", "%"),
    'Booster_Maneuverability_Regain_Time': ("Engine", "Boost Maneuverability Regain Time", "s"),
    'Booster_Power_Per-Second_Consumption': ("Engine", "Boost Power Consumption Per-Second", "pps"),
    'Booster_Speed_Multiplier': ("Engine", "Boost Speed Multiplier", "%"),
    'Crit_Chance_Reduction': ("Weapons", "Critical Hit Chance Reduction", "%"),
    'Engine_Base_Speed': ("Engine", "Speed Base", "m/s"),
    'Engine_Speed_Modifier_at_Max_Power': ("Engine", "Speed Maximum Modifier", "%"),
    'Engine_Speed_Modifier_at_Min_Power': ("Engine", "Speed Minimum Modifier", "%"),
    'Engine_Speed_Multiplier': ("Engine", "Speed Default Multiplier", "%"),
    'Engines_Max_Power': ("Engine", "Engine Power Capacity", "p"),
    'Max_Health': ("Hull_and_Shields", "Hull health", "p"),
    'Pitch': ("Maneuverability", "Pitch Turning Rate", "%"),
    'Power_Engine_Regen_Delay': ("Engine", "Engine Power Regeneration Delay", "s"),
    'Power_Engine_Regen_Rate': ("Engine", "Engine Power Regeneration Rate", "1f"),
    'Power_Engine_Regen_Rate_(when_Recently_Consumed)': ("Engine",
                                                         "Engine Power Regeneration Rate (Recently Consumed)", "pps"),
    'Power_Shield_Regen_Delay': ("Hull_and_Shields", "Shield Regeneration Delay", "s"),
    'Power_Shield_Regen_Rate': ("Hull_and_Shields", "Shield Regeneration Rate", "1f"),
    'Power_Shield_Regen_Rate_(when_Recently_Consumed)': ("Hull_and_Shields",
                                                         "Shield Regeneration Rate (Recently Consumed)", "pps"),
    'Power_Weapon_Regen_Delay': ("Weapons", "Weapon Power Regeneration Delay", "s"),
    'Power_Weapon_Regen_Rate': ("Weapons", "Weapon Power Regeneration Rate", "1f"),
    'Power_Weapon_Regen_Rate_(when_Recently_Consumed)': ("Weapons",
                                                         "Weapon Power Regeneration Rate (Recently Consumed)", "pps"),
    'Sensor_Communication_Range': ("Sensors", "Communication Range", "m"),
    'Sensor_Dampening': ("Sensors", "Dampening", "m"),
    'Sensor_Detection_Radius': ("Sensors", "Detection Radius", "m"),
    'Sensor_Focused_Detection_Arc': ("Sensors", "Focused Detection Arc", "°"),
    'Sensor_Focused_Detection_Range': ("Sensors", "Focused Detection Range", "m"),
    'Sensor_Signature': ("Sensors", "Signature", "bool"),
    'Shield_Bleed_Through': ("Hull_and_Shields", "Bleed-through", "%"),
    'Shield_Strength_Modifier_at_Default_Power': ("Hull_and_Shields", "Shield Strength (Default Power)", "%"),
    'Shield_Strength_Modifier_at_Max_Power': ("Hull_and_Shields", "Shield Strength (Max Power)", "%"),
    'Shield_Strength_Modifier_at_Min_Power': ("Hull_and_Shields", "Shield Strength (Min Power)", "%"),
    'Shields_Max_Power_(Capacity)': ("Hull_and_Shields", "Shield Maximum Power", "p"),
    'Ship_Damage_Reduction': ("Hull_and_Shields", "Damage Reduction", "%"),
    'Ship_Evasion': ("Hull_and_Shields", "Evasion", "%"),
    'Strafe_Modifier': ("Maneuverability", "Strafe Modifier", "%"),
    'Turn_Rate_Modifier': ("Maneuverability", "Turning Rate Modifier", "%"),
    'Weapon_Damage_Modifier_at_Default_Power': ("Weapons", "Primary Weapon Damage Modifier (Default Power)", "%"),
    'Weapon_Damage_Modifier_at_Max_Power': ("Weapons", "Primary Weapon Damage Modifier (Max Power)", "%"),
    'Weapon_Damage_Modifier_at_Min_Power': ("Weapons", "Primary Weapon Damage Modifier (Min Power)", "%"),
    'Weapon_Max_Power': ("Weapons", "Weapons Maximum Power", "p"),
    'Yaw': ("Maneuverability", "Yaw Turning Rate", "%"),
    'Ammo_Pool_Size': ("Missile", "Ammo", ""),
    'Crit_Chance': ("General", "Critical Hit Chance", "%"),
    'Crit_Damage_Multiplier': ("General", "Critical Damage Multiplier", "%"),
    'Weapon_Armor_Penetration': ("General", "Armor Penetration", "%"),
    'Weapon_Base_Accuracy': ("Accuracy", "Accuracy Base", "%"),
    'Weapon_Base_Damage': ("General", "Damage Base", "p"),
    'Weapon_Charge_Up_Time': ("Railgun", "Charge-Up Time", "s"),
    'Weapon_Cooldown_Time_(OBSOLETE)': ("General", "Cooldown Time", "s"),
    'Weapon_Firing_Arc': ("General", "Firing Arc", "°"),
    'Weapon_Hull_Damage_Multiplier': ("General", "Damage Hull Multiplier", "%"),
    'Weapon_Lock_On_Time': ("Missile", "Lock-On Time", "s"),
    'Weapon_Power_Draw': ("General", "Power Draw", "pps"),
    'Weapon_Range_Long': ("Range", "Range Long", "im"),
    'Weapon_Range_Mid': ("Range", "Range Mid", "im"),
    'Weapon_Range_Point_Blank': ("Range", "Range Close", "im"),
    'Weapon_Rate_of_Fire': ("General", "Rate of Fire", "sps"),
    'Weapon_Reload_Time': ("Missile", "Reload Time", "s"),
    'Weapon_Shield_Damage_Multiplier': ("General", "Damage Shield Multiplier", "%"),
    'Weapon_Shield_Piercing': ("General", "Shield Piercing", "%"),
    'longRangeAccMulti': ("Accuracy", "Long-Range Accuracy Multiplier", "%"),
    'longRangeDamMulti': ("General", "Damage Long-Range Multiplier", "%"),
    'midRangeAccMulti': ("Accuracy", "Mid-Range Accuracy Multiplier", "%"),
    'midRangeDamMulti': ("General", "Damage Mid-Range Multiplier", "%"),
    'pbRangeAccMulti': ("Accuracy", "Short-Range Accuracy Multiplier", "%"),
    'pbRangeDamMulti': ("General", "Damage Short-Range Multiplier", "%"),
    'trackingAccuracyLoss': ("Accuracy", "Tracking penalty", "%/°"),
    'Cooldown': ('General', 'Cooldown', 's'),
    'Active': ('General', 'Active Ability', 'bool'),
    'Booster_Speed': ("Engine", "Boost Speed", "m/s"),
    'Turning_Rate_Yaw': ("Engine", "Turning Rate Yaw", "%"),
    'Turning_Rate_Pitch': ("Engine", "Turning Rate Pitch", "%"),

    # Mine Stats
    'Mine_Armor_Penetration': ("", "", "%"),
    'Mine_Count': ("", "", "i"),
    'Mine_Crit_Chance': ("", "", "%"),
    'Mine_DOT': ("", "", "bool"),
    'Mine_DOT_Damage': ("", "", "p"),
    'Mine_DOT_Duration': ("", "", "s"),
    'Mine_Damage': ("", "", "p"),
    'Mine_Explosion_Damage': ("", "", "p"),
    'Mine_Explosion_Radius': ("", "", "m"),
    'Mine_Hull_Damage': ("", "", "%"),
    'Mine_Lifespan': ("", "", "s"),
    'Mine_Range': ("", "", "m"),
    'Mine_Shield_Damage': ("", "", "%"),
    'Mine_Shield_Piercing': ("", "", "%"),
    'Mine_Slow': ("", "", "bool"),
    'Mine_Slow_Duration': ("", "", "s"),
    'Mine_Slow_Effect': ("", "", "%"),
    "Mine_Explosion_Damage_Shields": ("", "", "i"),
    "Mine_Explosion_Damage_Hull": ("", "", "i")
}

STATISTICS.update({
    "Weapon_Damage_{}".format("{}_{}".format(range, target)): ("", "", "i")
    for range in ("Pb", "Mid", "Long") for target in ("Hull", "Shields")})
STATISTICS.update({"Weapon_Accuracy_{}".format(range): ("", "", "%") for range in ("Pb", "Mid", "Long")})
STATISTICS.update({"Power_{}_Regen_Rate_High".format(pool): ("", "", "1f") for pool in ("Engine", "Shield", "Weapon")})
STATISTICS.update({"Shield_Strength_{}".format(mode): ("", "", "i") for mode in ("Default", "Max", "Min")})
STATISTICS.update({"Engine_Speed_{}".format(mode): ("", "", "1f") for mode in ("Default", "Max", "Min")})


HULL_AND_SHIELDS_STATS_STRING = \
    "*Hull Health*: {Max_Health}\n" \
    "*Shield Power (Total) (F4-F2-Fx)*: {Shield_Strength_Default}-{Shield_Strength_Max}-{Shield_Strength_Min}p\n" \
    "*Shield Regen Rate*: {Power_Shield_Regen_Rate}pps\n" \
    "*Shield Regen Delay*: {Power_Shield_Regen_Delay}\n" \
    "*Shield Regen Rate (Recently Consumed)*: {Power_Shield_Regen_Rate_(when_Recently_Consumed)}\n" \
    "*Shield Bleed-through*: {Shield_Bleed_Through}\n" \
    "*Damage Reduction*: {Ship_Damage_Reduction}\n" \
    "*Evasion*: {Ship_Evasion}"


ENGINE_STATS_STRING = \
    "*Boost Acceleration*: {Booster_Acceleration}\n" \
    "*Boost Activation Power Cost*: {Booster_Activation_Power_Cost}\n" \
    "*Boost Maneuverability Modifier*: {Booster_Maneuverability_Modifier}\n" \
    "*Boost Maneuverability Regain Time*: {Booster_Maneuverability_Regain_Time}\n" \
    "*Boost Power Consumption*: {Booster_Power_Per-Second_Consumption}\n" \
    "*Boost Speed*: {Booster_Speed}\n" \
    "*Engine Speed (F4-F3-Fx)*: {Engine_Speed_Default}-{Engine_Speed_Max}-{Engine_Speed_Min}m/s\n" \
    "*Engine Power Capacity*: {Engines_Max_Power}\n" \
    "*Engine Power Regen Rate*: {Power_Engine_Regen_Rate}pps\n" \
    "*Engine Power Regen Delay*: {Power_Engine_Regen_Delay}\n" \
    "*Engine Power Regen Rate (Recently Consumed)*: {Power_Engine_Regen_Rate_(when_Recently_Consumed)}\n" \
    "*Turning Rate (Pitch, Yaw)*: {Turning_Rate_Pitch}, {Turning_Rate_Yaw}"

WEAPON_STATS_STRING = \
    "*Primary Weapon Damage (F4-F1-Fx)*: {Weapon_Damage_Modifier_at_Default_Power}, " \
                                        "{Weapon_Damage_Modifier_at_Max_Power}, " \
                                        "{Weapon_Damage_Modifier_at_Min_Power}\n" \
    "*Weapon Power Capacity*: {Weapon_Max_Power}\n" \
    "*Weapon Power Regen Rate*: {Power_Weapon_Regen_Rate}pps\n" \
    "*Weapon Power Regen Delay*: {Power_Weapon_Regen_Delay}\n" \
    "*Weapon Power Regen Rate (Recently Consumed)*: {Power_Weapon_Regen_Rate_(when_Recently_Consumed)}"

SENSOR_STATS_STRING = \
    "*Communication Range*: {Sensor_Communication_Range}\n" \
    "*Detection Radius*: {Sensor_Detection_Radius}\n" \
    "*Focused Detection Arc*: {Sensor_Focused_Detection_Arc}\n" \
    "*Focused Detection Range*: {Sensor_Focused_Detection_Range}\n" \
    "*Dampening*: {Sensor_Dampening}"

PRIMARY_WEAPON_STATS_STRING = \
    "*Range (short-mid-long)*: {Weapon_Range_Point_Blank}, " \
                              "{Weapon_Range_Mid}, " \
                              "{Weapon_Range_Long}m\n" \
    "*Shield Damage (short-mid-long)*: {Weapon_Damage_Pb_Shields}, " \
                                      "{Weapon_Damage_Mid_Shields}, " \
                                      "{Weapon_Damage_Long_Shields}p\n" \
    "*Hull Damage (short-mid-long)*: {Weapon_Damage_Pb_Hull}, " \
                                   "{Weapon_Damage_Mid_Hull}, " \
                                   "{Weapon_Damage_Long_Hull}p\n" \
    "*Shield Piercing*: {Weapon_Shield_Piercing}\n" \
    "*Armor Penetration*: {Weapon_Armor_Penetration}\n" \
    "*Critical Hit Chance*: {Crit_Chance}\n" \
    "*Critical Hit Damage*: {Crit_Damage_Multiplier}\n" \
    "*Accuracy (short-mid-long)*: {Weapon_Accuracy_Pb}, {Weapon_Accuracy_Mid}, {Weapon_Accuracy_Long}\n" \
    "*Firing Arc*: {Weapon_Firing_Arc}\n" \
    "*Tracking Penalty*: {trackingAccuracyLoss}\n"

AMMO_STRING = "*Ammo*: {Ammo_Pool_Size}\n"

MISSILE_STATS_STRING = \
    "*Hull Damage*: {Weapon_Damage_Long_Hull}p\n" \
    "*Shield Damage*: {Weapon_Damage_Long_Shields}p\n" \
    "*Armor Penetration*: {Weapon_Armor_Penetration}\n" \
    "*Shield Piercing*: {Weapon_Shield_Piercing}\n" \
    "*Firing Arc*: {Weapon_Firing_Arc}\n" \
    "*Lock-on Range* {Weapon_Range_Long}\n"  \
    "*Lock-on Time*: {Weapon_Lock_On_Time}\n" \
    "*Reload Time*: {Weapon_Reload_Time}\n" \
    "*Ammo_Pool_Size*: {Weapon_Ammo}"

RAILGUN_STATS_STRING = \
    "*Hull Damage*: {Weapon_Damage_Long_Hull}p\n" \
    "*Shield Damage*: {Weapon_Damage_Long_Shields}p\n" \
    "*Armor Penetration*: {Weapon_Armor_Penetration}\n" \
    "*Shield Piercing*: {Weapon_Shield_Piercing}\n" \
    "*Accuracy (normal, point blank)*: {Weapon_Base_Accuracy}, {Weapon_Accuracy_Pb}\n" \
    "*Tracking Penalty*: {trackingAccuracyLoss}\n" \
    "*Firing Arc*: {Weapon_Firing_Arc}\n" \
    "*Range (normal, point blank)*: {Weapon_Range_Long}, {Weapon_Range_Point_Blank}m\n" \
    "*Charge-up Time*: {Weapon_Charge_Up_Time}\n" \
    "*Cooldown*: {Weapon_Reload_Time}"

