import _pickle as pickle
from pprint import pformat


with open("companions.db", "rb") as fi:
    data = pickle.load(fi)

crew = dict()

for faction, faction_data in data.items():
    for role_dict in faction_data:
        role = list(role_dict.keys())[0]
        if role == "CoPilot":
            continue
        role_list = role_dict[role]
        for member_dict in role_list:
            name = member_dict["Name"]
            crew[name] = member_dict
            crew[name]["Faction"] = faction
            crew[name]["Category"] = role

with open("crew.db", "wb") as fo:
    pickle.dump(crew, fo)

with open("ships.db", "rb") as fi:
    data = pickle.load(fi)

components = dict()

component_keys = [
    "PrimaryWeapon",
    "SecondaryWeapon",
    "ShieldProjector",
    "Systems",
    "Magazine",
    "Engine",
    "Sensor",
    "Reactor",
    "Thruster",
    "Capacitor",
    "Armor"
]

for ship_name, ship_data in data.items():
    for category in ship_data:
        if category in component_keys:
            if category not in components:
                components[category] = list()
            components[category].extend(ship_data[category])
final = dict()
for category in components:
    final[category] = dict()
    for comp in components[category]:
        final[category][comp["Name"]] = comp
        final[category][comp["Name"]]["Category"] = category

with open("components.db", "wb") as fo, open("components.txt", "w") as plain:
    pickle.dump(final, fo)
    plain.write(pformat(final))
