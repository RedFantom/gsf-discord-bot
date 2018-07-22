"""
Author: RedFantom
License: GNU GPLv3 as in LICENSE
Copyright (C) 2018 RedFantom
"""
# Standard Library
from ast import literal_eval


class Strategy(object):
    """
    Simple data class to store the phases of a strategy and properties
    such as description and map
    """
    def __init__(self, name, map):
        """
        :param name: name of the Strategy
        :param map: map tuple (match_type, location)
        """
        self.name = name
        self.map = map
        self.phases = {}
        self.description = ""

    def __getitem__(self, item):
        if item is None:
            return self
        return self.phases[item]

    def __setitem__(self, key, value):
        if not isinstance(value, Phase):
            raise ValueError("Incompatible data type for Strategy: {0}".format(value))
        self.phases[key] = value

    def __iter__(self):
        for key, value in self.phases.items():
            yield key, value

    def __delitem__(self, key):
        del self.phases[key]

    def __contains__(self, item):
        return item in self.phases

    def serialize(self):
        """
        Function to serialize a Strategy object into a string

        Format:
        strategy_{name}~{description}~{(match_type, map_name)}~ \
            {phase_name}¤{phase_description}¤{(match_type, map_name)}¤
                {item_data: dict}³{item_data: dict}³{item_data: dict}¤
            ~
            ... phase ...
                ... items ...
        """
        # Strategy Data
        string = "strategy_" + self.name + "~" + self.description + "~" + str(self.map) + "~"
        # Phases
        for phase_name, phase in self:
            string += phase.name + "¤" + phase.description + "¤" + str(phase.map) + "¤"
            # Items
            for item_name, item in phase:
                string += "³" + str(item.data)
            string += "~"
        return string

    @staticmethod
    def deserialize(string):
        """Function to rebuild Strategy object from string"""
        strategy_elements = string.split("~")
        # strategy_elements: "strategy_{name}", description: str, map: tuple in str
        s_name, s_descr, s_map = strategy_elements[0:3]
        phases = strategy_elements[3:]
        # Generate a new Strategy Object
        strategy = Strategy(s_name, s_map)
        strategy.description = s_descr
        # Create the Phases for the Strategy from strings
        for phase_string in phases:
            if phase_string == "":
                continue
            # Phase string: {name}¤{description}¤{map_tuple}¤items_string
            phase_string_elements = phase_string.split("¤")
            # Elements: name, description, tuple, items_string
            phase_name, phase_description = phase_string_elements[0:2]
            phase_map = literal_eval(phase_string_elements[2])
            # Build a new Phase instance
            phase = Phase(phase_name, phase_map)
            phase.description = phase_description
            # Item string contains the items of the Phase
            item_string = phase_string_elements[3]
            item_elements = item_string.split("³")
            for item_string in item_elements:
                # item_string: "item_dictionary"
                if item_string == "":
                    continue
                item_dictionary = literal_eval(item_string)
                # Add the item to the Phase
                phase[item_dictionary["name"]] = Item(
                    item_dictionary["name"],
                    item_dictionary["x"],
                    item_dictionary["y"],
                    item_dictionary["color"],
                    item_dictionary["font"]
                )
            # Add the newly created Phase to the Strategy
            strategy[phase_name] = phase
        return strategy


class Phase(object):
    """Simple data class to store the Items of a Phase of a Strategy"""
    def __init__(self, name: str, map: tuple):
        """
        :param name: Phase name
        :param map: map tuple (match_type, location)
        """
        self.items = {}
        self.name = name
        self.map = map
        self.description = ""

    """
    These functions are similar to dictionary functionality
    """

    def __setitem__(self, key, value):
        if not isinstance(value, Item):
            raise ValueError("Incompatible data type for Phase: {0}".format(value))
        self.items[key] = value

    def __getitem__(self, key):
        return self.items[key]

    def __iter__(self):
        for key, value in self.items.items():
            yield key, value

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __delitem__(self, item):
        del self.items[item]


class Item(object):
    """
    Simple data class that provides a dictionary like interface with a
    limited functionality and a limited number of keys that can be used,
    so it does not store any more data than is required for an Item.
    """
    def __init__(self, name, x, y, color, font):
        """
        :param name: Item name
        :param x: Item location x coordinate
        :param y: Item location y coordinate
        :param color: HTML-color value
        :param font: font tuple (family, size, *options)
        """
        self.data = {
            "name": name,
            "x": x,
            "y": y,
            "color": color,
            "font": font
        }

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        if key not in self.data:
            raise KeyError("Invalid Item key: {}".format(key))
        self.data[key] = value
