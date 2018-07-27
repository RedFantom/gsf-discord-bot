"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
import os
import _pickle as pickle
from pprint import pprint
# Project Modules
from data.components import component_types, component_types_reverse, components
from parsing.ships import Ship, Component
from utils.utils import get_assets_directory, setup_logger


logger = setup_logger("ShipStats", "stats.log")


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
        self.calculate_ship_statistics()

    def calculate_ship_statistics(self):
        """Calculate the statistics of the Ship Object"""
        self.stats.clear()
        self.stats["Ship"] = self.ships_data[self.ship.ship_name]["Stats"].copy()
        # Go over components
        for category in components:
            category = component_types_reverse[category]
            # The categories are gone over in a certain order
            if category not in self.ship.components:
                continue
            component = self.ship.components[category]
            # If component is None, then the component is not correctly set
            if component is None:
                continue
            if not isinstance(component, Component):
                raise TypeError()
            category = component_types[category]
            # Get the data belonging to the component
            component_data = self.ships_data[self.ship.ship_name][category][component.index].copy()
            # Go over the upgrades for the component first
            base_stats = component_data["Base"]["Stats"].copy()
            if base_stats == {}:
                base_stats = component_data["Base"]
            self.stats[category] = component_data["Stats"].copy() if component_data["Stats"] != {} else base_stats
            for upgrade, state in component.upgrades.items():
                # Check the state first for efficiency
                if state is False:
                    continue
                # The upgrade can either be an index, or a tuple of indexes
                # The TalentTree of the component is built of lists
                if isinstance(upgrade, tuple):
                    # Tuple (upgrade_index, side_index)
                    upgrade_index, side_index = upgrade
                    upgrade_data = component_data["TalentTree"][upgrade_index][side_index].copy()
                else:
                    # upgrade_index
                    upgrade_data = component_data["TalentTree"][upgrade][0].copy()
                if not isinstance(upgrade_data, dict):
                    raise ValueError(
                        "upgrade_data was not a dict for category '{}' and upgrade index '{}': {}".format(
                            category, upgrade, upgrade_data
                        )
                    )
                # upgrade_data now contains a dictionary of data of the upgrade
                upgrade_data["Target"] = upgrade_data["Target"].replace("0x00", "")
                # Go over the statistics of the upgrade
                for stat, value in upgrade_data["Stats"].items():
                    statistic, multiplicative = ShipStats.is_multiplicative(stat)
                    if upgrade_data["Target"] == "":
                        if statistic in self.ALIASES:
                            statistic = self.ALIASES[statistic]
                        if statistic in base_stats:
                            base_stats = ShipStats.update_statistic(
                                base_stats, statistic, multiplicative, value
                            )
                        elif statistic in self.stats["Ship"]:
                            self.stats["Ship"] = ShipStats.update_statistic(
                                self.stats["Ship"], statistic, multiplicative, value
                            )
                        else:
                            logger.error("Invalid statistic: {}".format(statistic))
                    elif upgrade_data["Target"] == "Self":
                        self.stats[category] = ShipStats.update_statistic(
                            self.stats[category], statistic, multiplicative, value
                        )
                    elif upgrade_data["Target"] == "PrimaryWeapons" or upgrade_data["Target"] == "SecondaryWeapons":
                        key = upgrade_data["Target"][:-1]
                        for key in (key, key+"2"):
                            if key not in self.stats:
                                continue
                            self.stats[key] = ShipStats.update_statistic(
                                self.stats[key], statistic, multiplicative, value
                            )
                    else:
                        raise ValueError("Unknown upgrade target found: {}".format(upgrade_data["Target"]))
            # These are the statistics to go over
            component_stats = base_stats
            for stat, value in component_stats.items():
                if not isinstance(value, (int, float)):
                    continue
                # Process the statistic name
                statistic, multiplicative = ShipStats.is_multiplicative(stat)
                # Perform the calculation
                for category_to_update in self.stats.keys():
                    if category == "Capacitor" and "PrimaryWeapon" not in category_to_update:
                        continue  # Exception for Capacitors as data is missing
                    if statistic not in self.stats[category_to_update]:
                        continue
                    self.stats[category_to_update] = ShipStats.update_statistic(
                        self.stats[category_to_update], statistic, multiplicative, value
                    )
        # Go over Crew
        for category, companion in self.ship.crew.items():
            if category == "CoPilot" or companion is None:
                continue
            member_data = self.get_crew_member_data(*companion)
            for stats in (member_data["PassiveStats"], member_data["SecondaryPassiveStats"]):
                for stat, value in stats.items():
                    statistic, multiplicative = ShipStats.is_multiplicative(stat)
                    for category in self.stats.keys():
                        if statistic not in self.stats[category]:
                            continue
                        self.stats[category] = ShipStats.update_statistic(
                            self.stats[category], statistic, multiplicative, value
                        )
        pprint(self.stats)

    """
    Functions to process statistics
    """

    @staticmethod
    def update_statistic(statistics, statistic, multiplicative, value):
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

