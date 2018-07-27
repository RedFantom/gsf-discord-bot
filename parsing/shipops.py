"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from collections import namedtuple
from math import ceil, floor
# Project Modules
from parsing.ships import Ship
from parsing.shipstats import ShipStats
from utils.utils import setup_logger

RANGES = ["Weapon_Range_Point_Blank", "Weapon_Range_Mid", "Weapon_Range_Long"]
DMG_MODS = ["pbRangeDamMulti", "midRangeDamMulti", "longRangeDamMulti"]
ACC_MODS = ["pbRangeAccMulti", "midRangeAccMulti", "longRangeAccMulti"]
SH_MOD, HULL_MOD = "Weapon_Shield_Damage_Multiplier", "Weapon_Hull_Damage_Multiplier"
SH_PIERCING = "Weapon_Shield_Piercing"
SPS = "Weapon_Rate_of_Fire"
CRIT_CHANCE, CRIT_MOD = "Crit_Chance", "Crit_Damage_Multiplier"
SH_HEALTH, HULL_HEALTH = "Shields_Max_Power_(Capacity)", "Max_Health"


logger = setup_logger("shipops", "ships.log")

TimeToKill = namedtuple("TimeToKill", ("shots", "time", "distance", "weapon", "actives"))


class InfiniteShots(ValueError):
    pass


def linear(point1: tuple, point2: tuple, x: float):
    """Given a linear approximation using two points"""
    (x1, y1), (x2, y2) = point1, point2
    return y1 + (x - x1) * ((y2 - y1) / (x2 - x1))


def get_range_adjusted_dmg(stats: dict, distance: float)->tuple:
    """Return range adjusted base hull and base shield damage of weapon"""
    pb, mid, long = ranges = tuple(map(stats.get, RANGES))
    mods = tuple(map(stats.get, DMG_MODS))
    base_dmg = stats["Weapon_Base_Damage"]
    pb_dmg, mid_dmg, long_dmg = range_dmgs = tuple(map(lambda x: base_dmg * x, mods))
    point1, point2, point3 = tuple(zip(ranges, range_dmgs))
    if distance <= pb:
        base_dmg = pb_dmg
    elif pb < distance <= mid:
        base_dmg = linear(point1, point2, distance)
    elif mid < distance <= long:
        base_dmg = linear(point2, point3, distance)
    else:
        raise InfiniteShots()
    hull_mod, sh_mod = stats[HULL_MOD], stats[SH_MOD]
    hull_dmg, sh_dmg = tuple(map(lambda x: base_dmg * x, (hull_mod, sh_mod)))
    return hull_dmg, sh_dmg


def get_range_adjusted_acc(stats: dict, distance: float)->float:
    """Return range adjusted accuracy statistic"""
    pb, mid, long = ranges = tuple(map(stats.get, RANGES))
    mods = tuple(map(stats.get, ACC_MODS))
    logger.debug("Accuracy mods: {}, {}, {}".format(*mods))
    base_acc = stats["Weapon_Base_Accuracy"]
    logger.debug("Base accuracy: {}".format(base_acc))
    pb_acc, mid_acc, long_acc = range_accs = tuple(map(lambda x: base_acc + x, mods))
    logger.debug("Accuracies: {}, {}, {}".format(*range_accs))
    point1, point2, point3 = tuple(zip(ranges, range_accs))
    if distance <= pb:
        return pb_acc
    elif pb < distance <= mid:
        return linear(point1, point2, distance)
    elif mid < distance <= long:
        return linear(point2, point3, distance)
    else:
        raise InfiniteShots()


def get_crit_adjusted_damage(stats: dict, hull_dmg: float, sh_dmg: float) -> tuple:
    """Return crit damage for hull and shields and crit chance"""
    chance, mod = map(stats.get, (CRIT_CHANCE, CRIT_MOD))
    if mod < 1.0:
        mod += 1.0
    return tuple(map(lambda x: mod * x, (hull_dmg, sh_dmg))) + (chance,)


def get_time_to_kill(source: Ship, target: Ship, distance: float,
                     source_act: list, target_act: list, key="PrimaryWeapon") -> (TimeToKill, None):
    """Calculate the time to kill of one ship against another"""
    actives = dict()
    if not isinstance(source, ShipStats) and not isinstance(target, ShipStats):  # acc optimization
        source, target = ShipStats(source), ShipStats(target)
        actives["source"] = source.apply_actives(source_act)
        actives["target"] = target.apply_actives(target_act)
    # Get the base statistics
    if key not in source:
        return None
    hull_d_reg, sh_d_reg = get_range_adjusted_dmg(source[key], distance)
    hull_d_crit, sh_d_crit, crit_chance = get_crit_adjusted_damage(source[key], hull_d_reg, sh_d_reg)
    sh_piercing, sps = map(source[key].get, (SH_PIERCING, SPS))
    target_hull, target_shields = map(target["Ship"].get, (HULL_HEALTH, SH_HEALTH))
    bleedthrough = target["Ship"]["Shield_Bleed_Through"]
    sh_piercing = bleedthrough + sh_piercing - bleedthrough * sh_piercing
    # Return get_time_to_kill_stats
    avg_ttk, avg_shots = get_time_to_kill_stats(
        hull_d_reg, hull_d_crit, sh_d_reg, sh_d_crit, sps, crit_chance,
        sh_piercing, target_hull, target_shields)
    logger.debug("Input values: {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
        hull_d_reg, hull_d_crit, sh_d_reg, sh_d_crit, sps, crit_chance,
        sh_piercing, target_hull, target_shields))
    logger.debug("Calculated result {}, {}, {}".format(avg_ttk, avg_shots, distance))
    return TimeToKill(ceil(avg_shots), avg_ttk, distance, key, actives)


def get_time_to_kill_acc(
        source: Ship, target: Ship, distance: float, source_act: list, target_act: list,
        key="PrimaryWeapon") -> (TimeToKill, None):
    """Calculate the time to kill with evasion/accuracy correction"""
    source, target = map(ShipStats, (source, target))
    actives = dict()
    actives["source"] = source.apply_actives(source_act)
    actives["target"] = source.apply_actives(target_act)
    evs = target["Ship"]["Ship_Evasion"]
    acc = get_range_adjusted_acc(source[key], distance)
    hit = acc - evs
    if hit == 0 or hit < 0:
        logger.debug("Accuracy minus evasion is zero! {}, {}".format(acc, evs))
        raise InfiniteShots()
    ttk = get_time_to_kill(source, target, distance, source_act, target_act, key=key)
    time, shots = tuple(map(lambda x: x * hit, (ttk.time, ttk.shots)))
    ttk = TimeToKill(time, ceil(shots), ttk.distance, ttk.weapon, actives)
    return ttk


def get_time_to_kill_stats(hull_d_reg, hull_d_crit, sh_d_reg, sh_d_crit, sps,
                           crit_chance, sh_piercing, target_hull, target_shields):
    """
    This code is based upon MATLAB code written by Close-shave.

    Function: function [avg_shots, avg_ttk] = TTK(reg_h, crit_h, reg_s, crit_s, sps, aCC, aSP, hull, shields)

    regular_x, average_x and critical_x are all damage numbers!
    """
    # avg_h = reg_h * (1 - aCC) + crit_h * aCC;
    # avg_s = reg_s * (1 - aCC) + crit_s * aCC;
    avg_h = hull_d_reg * (1 - crit_chance) + hull_d_crit * crit_chance
    avg_s = sh_d_reg * (1 - crit_chance) + sh_d_crit * crit_chance
    logger.debug("Average values: {:.1f}, {:.1f}".format(avg_h, avg_s))
    # if avg_h == 0;
    #    avg_shots = 'too long';
    #    avg_ttk = 'too long';
    #    return
    # end
    if avg_h == 0:
        raise ZeroDivisionError
    # if floor(shields/(avg_s * (1 - aSP))) * aSP * avg_h >= hull
    #     shield_sh = ceil(hull/(avg_h * aSP));
    # else
    #     shield_sh = floor(shields/(avg_s * (1 - aSP)));
    # end
    if floor(target_shields / (avg_s * (1 - sh_piercing))) * sh_piercing * avg_h >= target_hull:
        shield_shot = ceil(target_hull / (avg_h * sh_piercing))
    else:
        shield_shot = floor(target_shields / (avg_s * (1 - sh_piercing)))
    # if floor(shields/(avg_s * (1 - aSP))) * aSP * avg_h >= hull
    #     hull_sh = 0;
    # else
    #     hull_sh = ceil(hull - floor(shields / (avg_s * (1 - aSP)))* aSP * avg_h - \
    #                                                    (1 - (shields - shield_sh * avg_s * (1 - aSP))/avg_s))/ avg_h
    # end
    if floor(target_shields / (avg_s * (1 - sh_piercing))) * sh_piercing * avg_h >= target_hull:
        hull_shot = 0
    else:
        hull_shot = ceil(target_hull - floor(target_shields / (avg_s * (1 - sh_piercing)))
                         * sh_piercing * avg_h - (1 - (target_shields - shield_shot * avg_s *
                         (1 - sh_piercing)) / avg_s)) / avg_h
    # if floor(shields/(avg_s * (1 - aSP))) * aSP * avg_h >= hull
    #    border_sh = 0;
    # else
    #    if 1 - (shields - shield_sh * avg_s * (1 - aSP))/hull_sh > 0
    #        border_sh = 1;
    #    else
    #        border_sh = 0;
    #    end
    # end
    if floor(target_shields / (avg_s * (1 - sh_piercing))) * sh_piercing * avg_h >= target_hull:
        border_shot = 0
    elif 1 - (target_shields - shield_shot * avg_s * (1 - sh_piercing)) / hull_shot > 0:
        border_shot = 1
    else:
        # This could be combined into a single if/else
        border_shot = 0
    # avg_shots = shield_sh + border_sh + hull_sh;
    # avg_ttk = avg_shots / sps;
    average_shots = shield_shot + border_shot + hull_shot
    average_ttk = average_shots / sps
    # end
    return average_ttk, average_shots
