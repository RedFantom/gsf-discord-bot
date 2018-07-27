"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
import _pickle as pickle
# Project Modules
from data.actives import ACTIVES
from data.components import COMPONENT_TYPES, COMP_TYPES_REVERSE, COMPONENTS
from parsing.ships import Ship, Component
from utils.utils import get_assets_directory, setup_logger

logger = setup_logger("ShipStats", "stats.log")


class ActiveNotFound(KeyError):
    pass


class ActiveNotSupported(ValueError):
    pass


class ActiveNotAvailable(KeyError):
    pass


class ShipStats(object):
    """
    Class to calculate the statistics for a given ship object. Uses the
    data found in the databases to calculate statistics for the main
    ship and each component.
    """

    ALIASES = {
        "Cooldown_Time": "Cooldown",
    }

    def __init__(self, ship):
        """
        :param ship: Ship object
        """
        if not isinstance(ship, Ship):
            raise ValueError("ShipStats can only be initialized with a Ship object")
        self.stats = {}
        self.ship = ship
        with open(os.path.join(get_assets_directory(), "ships.db"), "rb") as fi:
            ships_data = pickle.load(fi)
        with open(os.path.join(get_assets_directory(), "companions.db"), "rb") as fi:
            companions_data = pickle.load(fi)
        self.ships_data = ships_data.copy()
        self.companions_data = companions_data.copy()
        self.calc_ship_stats()

    def calc_ship_stats(self):
        """Calculate the statistics of the Ship Object"""
        self.stats.clear()
        self.stats["Ship"] = self.ships_data[self.ship.ship_name]["Stats"].copy()
        self.calc_comp_stats()
        self.calc_crew_stats()

    def calc_comp_stats(self):
        """Calculate component stats and apply them"""
        for category in COMPONENTS:
            category = COMP_TYPES_REVERSE[category]
            if category not in self.ship.components:
                continue
            component = self.ship.components[category]
            if component is None:  # Component not set for this ship
                continue
            self.apply_comp_stats(component)

    def apply_comp_stats(self, comp: Component):
        """Apply the stats of a component in a category"""
        ctg = COMPONENT_TYPES[comp.category]
        data = self.ships_data[self.ship.ship_name][ctg][comp.index].copy()
        # Get the base statistics for this component
        base = data["Base"]["Stats"]
        base.update(data["Stats"])
        base["Cooldown"] = data["Base"]["Cooldown"]
        self.stats[ctg] = base.copy()
        # Apply enabled upgrades
        for u in (u for u in comp.upgrades.keys() if comp.upgrades[u] is True):
            i, s = u  # index, side
            upgrade = data["TalentTree"][i][s].copy()
            upgrade["Target"] = upgrade["Target"].replace("0x00", "")  # Inconsistency in data files
            # Apply statistics found in this upgrade
            target = upgrade.pop("Target", None)
            target = target if target != "Self" else ctg
            self.apply_stats(target, upgrade)
        # Apply statistics of the base component
        self.apply_stats("Ship", base)

    def calc_crew_stats(self):
        """Apply Crew Passive ability stats to self"""
        for category, companion in self.ship.crew.items():
            if category == "CoPilot" or companion is None:
                continue
            member_data = self.get_crew_member_data(*companion)
            for stats in (member_data["PassiveStats"], member_data["SecondaryPassiveStats"]):
                for stat, value in stats.items():
                    self.apply_stat_guess(stat, value)

    def apply_stats(self, target: (str, None), stats: dict):
        """Apply a dictionary of statistics"""
        for stat, val in stats.items():
            self.apply_stat(target, stat, val)

    def apply_stat(self, target: (str, None), stat: str, val: float):
        """Apply a statistic to a specific target"""
        if stat in self.ALIASES:
            stat = self.ALIASES[stat]
        if target is None:
            self.apply_stat_guess(stat, val)
        else:
            self.apply_stat_ctg(target, stat, val)

    def apply_stat_guess(self, stat: str, val: float):
        """Guess the correct dictionary for a statistic to be applied to"""
        stat, mul = self.is_multiplicative(stat)
        # Ship statistics take priority
        if stat in self["Ship"]:
            self.stats["Ship"] = self.update_stat(self.stats["Ship"], stat, mul, val)
            return
        # Weapons
        for set in (("PrimaryWeapon", "PrimaryWeapon2"), ("SecondaryWeapon", "SecondaryWeapon2")):
            applied = False
            for key in set:
                if key not in self.stats:
                    continue
                if stat in self.stats[key]:
                    self.stats[key] = self.update_stat(self.stats[key], stat, mul, val)
                    applied = True
            if applied is True:
                break
        logger.error("Could not determine correct stats dict for: {}".format(stat))

    def apply_stat_ctg(self, category: str, stat: str, val: float):
        """Apply a statistic to a given category"""
        if category == "":
            category = "Ship"
        elif category[-1] == "s":
            category = category[:-1]
            for ctg in (category, category + "2"):
                self.apply_stat_ctg(ctg, stat, val)
            return
        if category not in self.stats:
            return
        stat, mul = self.is_multiplicative(stat)
        self.stats[category] = self.update_stat(self.stats[category], stat, mul, val)

    def apply_actives(self, actives: list) -> list:
        """Apply a list of active abilities to self"""
        applied = list()
        for active in actives:
            # Name matching
            active_dict, key = False, None
            for key, dict in ACTIVES.items():
                if key.startswith(active):
                    active_dict = dict
                    break
                initials = "".join(l for l in key if l.isupper())
                if initials.lower() == active.lower():
                    active_dict = dict
                    break
            if active_dict is False:
                raise ActiveNotFound()
            elif active_dict is None:
                raise ActiveNotSupported()
            self.apply_active(key, active_dict)
            applied.append(key)
        return applied

    def apply_active(self, name: str, active: dict):
        """Apply an active ability to self"""
        talent_tree = active.pop("TalentTree", None)
        # Apply upgradess first
        if talent_tree is not None:
            if name not in (component.name for component in self.ship.components.values() if component is not None):
                raise ActiveNotAvailable()
            component = list(component for component in self.ship.components.values()
                             if component is not None and component.name == name)[0]
            assert isinstance(component, Component)
            upgrades = (upgrade for upgrade in component.upgrades if component.upgrades[upgrade] is True)
            for upgrade in upgrades:
                assert upgrade in talent_tree
                upgrade = talent_tree[upgrade]
                assert isinstance(upgrade, dict)
                target = upgrade.pop("Target", None)
                if target is None:
                    for stat, val in upgrade.items():
                        self.apply_stat("Ship", stat, val)
                elif target == "self":
                    for stat, val in upgrade.items():
                        stat, mul = self.is_multiplicative(stat)
                        active = self.update_stat(active, stat, mul, val)
                else:
                    self.apply_stats(target, upgrade)
        # Apply component statistics that were updated with upgrades
        self.apply_stats(None, active)

    """
    Functions to process statistics
    """

    @staticmethod
    def update_stat(statistics: dict, statistic: str, multiplicative: bool, value: float):
        """
        Update a statistic in a dictionary
        :param statistics: statistics dictionary
        :param statistic: statistic name
        :param multiplicative: bool statistic is multiplicative
        :param value: value to update with
        :return: new statistics dictionary
        """
        if statistic not in statistics:
            return statistics
        if multiplicative is True:
            statistics[statistic] *= value + 1
        else:
            statistics[statistic] += value
        return statistics

    @staticmethod
    def is_multiplicative(statistic):
        """
        Determine whether a statistic is multiplicative or not
        :param statistic: statistic name
        :return: real statistic name str,  multiplicative bool
        """
        multiplicative = "[Pc]" in statistic
        statistic = statistic.replace("[Pc]", "").replace("[Pb]", "")
        return statistic, multiplicative

    def get_crew_member_data(self, faction, category, name):
        faction_data = self.companions_data[faction]
        category_data = [item for item in faction_data if category in item][0][category]
        member_data = [item for item in category_data if item["Name"] == name][0]
        return member_data.copy()

    # Dictionary like functions

    def __getitem__(self, item):
        return self.stats[item]

    def __setitem__(self, item, value):
        self.stats[item] = value

    def __contains__(self, item):
        return item in self.stats

    def __iter__(self):
        """Iterator for all of the statistics and their values"""
        for key, value in self.stats.items():
            yield key, value
