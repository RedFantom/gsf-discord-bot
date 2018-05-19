"""
Author: RedFantom
Contributors: Daethyra (Naiii) and Sprigellania (Zarainia)
License: GNU GPLv3 as in LICENSE
Copyright (C) 2016-2018 RedFantom
"""
# Standard Library
from os import path
import pickle as pickle
# Project Modules
from data import abilities
from data.components import *
from data.crew import crew
from data.ships import ship_names, ships_names_reverse, ship_tier_factions
from utils.utils import get_assets_directory


def get_ship_category(ship_name: str):
    """Return the ship category for a given ship name"""
    with open(path.join(get_assets_directory(), "categories.db"), "rb") as fi:
        categories = pickle.load(fi)
    ship_name = ship_name if ship_name not in ship_names else ship_names[ship_name]
    faction = ship_name.split("_")[0]
    ship_name = ship_name.replace("Imperial_", "").replace("Republic_", "")
    categories = categories[faction]
    for category in categories:
        ships = categories[category]["Ships"]
        for ship in ships:
            if ship["JsonPath"].replace(".json", "") == ship_name:
                return category["CategoryName"]
    return None


def load_ship_data()->dict:
    with open(path.join(get_assets_directory(), "ships.db"), "rb") as f:
        ships_data = pickle.load(f)
    return ships_data


class Ship(object):
    """
    Data class that contains the data required to perform calculations
    for and operations on GSF Ships. For every Ship, the components and
    selected crew members are selected.

    :attribute name: Simple ship name
    :attribute ship_name: Fully-Qualified Ship name
    """

    def __init__(self, ship_name: str):
        """
        :param ship_name: FQ or Simple ship name
        """
        ships_data = load_ship_data()
        # Find FQN and simple ship name
        self.ship_name = ship_name if ship_name in ships_data else ship_names[ship_name]  # FQN
        self.faction = self.ship_name.split("_")[0]
        self.name = ship_name if ship_name in ship_names else ships_names_reverse[self.ship_name]
        # Initialize attributes
        self.data = ships_data[self.ship_name]
        self.components = {
            "primary": None,
            "primary2": None,
            "secondary": None,
            "secondary2": None,
            "engine": None,
            "shields": None,
            "systems": None,
            "armor": None,
            "reactor": None,
            "magazine": None,
            "sensors": None,
            "thrusters": None,
            "capacitor": None
        }
        self.crew = {
            "Engineering": None,
            "Offensive": None,
            "Tactical": None,
            "Defensive": None,
            "CoPilot": None
        }

    def update_element(self, element: str, ships_data: (dict, None))->str:
        """
        Update an element of this ship with a string

        The element should be given in either of the following formats:
            category_short_hand/full_component_name/upgrades;
            crew/full_category/full_name;
        """
        if ships_data is None:
            ships_data = load_ship_data()
        element = element.strip(";")
        if element.startswith("crew"):  # Crew member!
            try:
                category, name = element.split("/")
            except ValueError:
                raise ValueError("Invalid crew member element string: `{}`".format(element))
            # Category and name matching
            match = False
            for role, members in crew[self.faction].items():
                if category in role:
                    for member in members:
                        if name in member:
                            category = role
                            name = member
                            match = True
                            break
            if match is False:
                raise ValueError("Invalid crew member name or category identifier")
            self[category] = (self.faction, category, name)
            return "{} now set to {}.".format(category, name)
        # shorthandcategory/fullname/upgrades;
        elems = element.split("/")
        if len(elems) == 2:
            category, name = elems
            upgrades = ""
        elif len(elems) == 3:
            category, name, upgrades = elems
        else:
            raise ValueError("Invalid component element string: `{}`".format(element))
        category = self.identify_component_category(category)
        name = self.identify_component_shorthand(name, category)
        category = component_types[category]
        if category not in ships_data[self.ship_name]:
            raise ValueError("Component category '{}' not available for ship '{}'".format(category, self.name))
        category_list = ships_data[self.ship_name][category]
        i = -1
        for j, component in enumerate(category_list):
            if component["Name"] == name:
                i = j
                break
        if i == -1:
            raise ValueError("Invalid component '{}' for ship '{}'".format(name, self.name))
        component = Component(ships_data[self.ship_name][category][i], i, category)
        component.upgrades.update(Ship.parse_upgrade_string(upgrades))
        self[category] = component
        return "{} now set to {}.".format(category, component)

    def __setitem__(self, item: str, value):
        """
        Update a given Component or Crew
        :param item: Component or Crew category
        :param value: Component instance or Crew member name
        """
        print("[Ship] Setting {} to {} for Ship {}".format(item, value, self.ship_name))
        item = self.process_key(item)
        if item in self.components:
            self.components[item] = value
        elif item in self.crew:
            self.crew[item] = value
        else:
            raise ValueError("Invalid key for Ship: '{}'".format(item))

    def __getitem__(self, item):
        """Returns a Component instance or Crew member name"""
        item = self.process_key(item)
        if item in self.components:
            return self.components[item]
        elif item in self.crew:
            return self.crew[item]
        raise KeyError("Invalid key for [Ship] instance: {}".format(item))

    def __iter__(self):
        for key, value in self.data.items():
            yield (key, value)

    def __contains__(self, item):
        return item in self.components or item in self.crew

    def process_key(self, item):
        """
        Not all keys may be appropriate for usage in components
        dictionary. The categories used in the data dictionary differ
        from those used in this Ship.components dictionary, and thus,
        must be translated appropriately.
        """
        if item in component_types_reverse:
            return component_types_reverse[item]
        elif item.lower() in self.components:
            item = item.lower()
        elif item in component_short_hand:
            return component_short_hand[item]
        return item

    def update(self, dictionary):
        for key, value in dictionary.items():
            self[key] = value

    def iter_components(self):
        for key, value in self.components.items():
            yield (key, value)

    def serialize(self)->str:
        """
        Serialize a Ship instance into a database-storage string

        Format:
            Fully-Qualified Ship Name;
            component_category_short_hand/index/upgrades
        """
        string = self.ship_name + ";" # FQN
        for key, component in self.components.items():
            # component is None or Component instance
            if component is None or not isinstance(component, Component):
                continue
            # Serialize the Component
            upgrades = Ship.build_upgrade_string(component.upgrades, component.type)
            comp = "{}/{}/{};".format(key, component.name, upgrades)
            string += comp
        for role, member in self.crew.items():
            if member is None:
                continue
            faction, role, name = member
            crew = "crew/{}/{};".format(role, name)
            string += crew
        return string

    @staticmethod
    def deserialize(string: str):
        """
        Build a Ship instance from a serialized string

        This is a rather complicated bit.
        """
        ships_data = load_ship_data()
        elements = string.split(";")
        # First element is FQSN
        ship_name = elements[0]
        ship = Ship(ship_name)
        # The string may only contain the ship name
        if len(elements) == 1:
            return ship
        # There are components and crew members to parse
        for element in elements[1:]:
            if element == "":
                continue
            ship.update_element(element, ships_data)
        return ship

    @staticmethod
    def build_upgrade_string(upgrades: dict, type: str):
        """Build an upgrades string"""
        if type not in abilities.upgrades:
            raise ValueError("Invalid component type (major/middle/minor)")
        string = str()
        for upgrade in abilities.upgrades[type]:
            if upgrades[upgrade] is True:
                if isinstance(upgrade, tuple):
                    _, side = upgrade
                    string += "L" if side == 0 else "R"
                    continue
                string += str(upgrade + 1)
                continue
            # The upgrade is not set
            break
        return string

    @staticmethod
    def parse_upgrade_string(upgrades: str):
        """Parse a specific upgrade string"""
        dictionary = dict()
        for level, letter in enumerate(upgrades):
            if letter.isdigit():
                dictionary[level] = True
                continue
            # letter is a Letter!
            side = {"L": 0, "R": 1}[letter]
            dictionary[(level, side)] = True
        return dictionary

    @staticmethod
    def identify_component_shorthand(shorthand: str, category: str):
        """
        Identify the component by its shorthand and return the full name
        """
        category = category.replace("2", str())
        shorthand = shorthand.lower()
        category = getattr(abilities, category)
        if shorthand in category:
            return category[shorthand]
        for key, value in category.items():
            if key.startswith(shorthand):
                return value
            if value.lower().startswith(shorthand):
                return value
        for _, value in category.items():
            key = str().join(word[0].lower() for word in value.split(" "))
            if key == shorthand:
                return value
        raise ValueError("Invalid component name shorthand: {}".format(shorthand))

    @staticmethod
    def identify_component_category(category: str):
        if category in shorthand_to_ship_key:
            return shorthand_to_ship_key[category]
        for key, to_match in component_short_hand.items():
            if category in to_match:
                return shorthand_to_ship_key[key]
        raise ValueError("Invalid component category identifier: {}".format(category))

    @staticmethod
    def from_base(base: str):
        if base not in ship_tier_factions:
            raise ValueError("Invalid ship base identifier: {}".format(base))
        name = ship_tier_factions[base]
        fqsn = ship_names[name]
        return Ship(fqsn)


class Component(object):
    """
    The Component class supports the storage of attributes for
    Components in a Ship.

    :attribute index: Index in ships.db[ship_name][category][index]
        is the component data dictionary
    :attribute category: Component category
    :attribute name: Component name
    :attribute upgrades: Upgrade dictionary
    """

    def __init__(self, data, index, category):
        """
        :param data: Component data dictionary
        :param index: Component index in this category
        :param category: Component category
        """
        self.index = index
        self.category = category
        self.name = data["Name"]
        self.upgrades = {
            0: False,
            1: False,
            2: False,
            (2, 0): False,
            (2, 1): False,
            (3, 0): False,
            (3, 1): False,
            (4, 0): False,
            (4, 1): False
        }
        for category in component_types.keys():
            category = category.replace("2", str())
            if self.name in getattr(abilities, category):
                for type in ["majors", "middle", "minors"]:
                    if category in getattr(abilities, type):
                        self.type = type.replace("s", str())
                        break
                if hasattr(self, "type"):
                    break
        if not hasattr(self, "type"):
            raise ValueError("Invalid component: {}".format(self.name))

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            tier, upgrade = map(int, key)
            if upgrade is 0:
                if self[(tier, 1)]:
                    self.upgrades[(tier, 1)] = False
                elif self[(tier, 0)]:
                    return
                else:
                    pass
            elif upgrade is 1:
                if self[(tier, 0)]:
                    self.upgrades[(tier, 1)] = False
                elif self[(tier, 1)]:
                    return
                else:
                    pass
            else:
                raise ValueError("Invalid value passed in tuple key: {0}".format(key))
        self.upgrades[key] = value

    def __getitem__(self, key):
        return self.upgrades[key]

    def __iter__(self):
        for key, value in self.upgrades.items():
            yield key, value
