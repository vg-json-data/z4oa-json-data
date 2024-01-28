import json
import os
from resources.ci.common.autoformat import autoformat
from string import ascii_uppercase

dirs = [
    os.path.join("region","labrynna","past"),
    os.path.join("region","labrynna","present")
]
for dirname in dirs:
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

for i in range(14):
    for j in range(14):
        region_path = os.path.join("region","labrynna","present",f"{ascii_uppercase[i]}{j}.json")
        if not os.path.isfile(region_path):
            with open(region_path, "w") as region_file:
                region_json = {
                    "$schema": "../../../schema/z3oa-room.schema.json",
                    "id": f"{ascii_uppercase[i]}{j}",
                    "name": "",
                    "area": "Labrynna",
                    "subarea": "",
                    "time": "Present",
                    "nodes": [
                        { "id": 1, "name": "", "nodeType": "", "nodeSubType": "", "nodeAddress": "" },
                        { "id": 2, "name": "", "nodeType": "", "nodeSubType": "", "nodeAddress": "" }
                    ],
                    "enemies": [],
                    "links": [
                        { "from": 1, "to": [ { "id": 2 } ] }
                    ],
                    "strats": [
                        { "link": [1, 2], "name": "Base", "requires": [] }
                    ]
                }
                region_file.write(json.dumps(region_json))
autoformat()
