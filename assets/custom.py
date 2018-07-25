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

with open("crew.txt", "w") as fo:
    fo.write(pformat(crew))
