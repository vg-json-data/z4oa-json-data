# pylint: disable=unnecessary-pass
"""
Validate JSON against provided schema
"""
import os
import json
import re
from pathlib import Path
import jsonschema.validators
from jsonschema.validators import Draft7Validator
from jsonschema import validate, RefResolver
from jsonschema import exceptions as JSONSchemaExceptions

schemas = {}

errors = []
bail = False

print("LOAD SCHEMAS")
schemaDir = os.path.join(".", "schema")
schemaAbsPath = os.path.abspath(schemaDir)
schemaURI = Path(schemaAbsPath).as_uri() + "/"
for schemaFileName in os.listdir(schemaDir):
    with open(
        os.path.join(
            schemaDir,
            schemaFileName
        ),
        "r",
        encoding="utf-8"
    ) as schemaFile:
        match = re.match(
            r"^([^-]*)(?:-)([^\.]*)(?:\.schema\.json)$",
            schemaFileName
        )
        if match:
            gameKey = match.group(1)
            schemaKey = match.group(2)
            if gameKey not in schemas:
                schemas[gameKey] = {}
            try:
                schemas[gameKey][schemaKey] = json.load(schemaFile)
            except json.JSONDecodeError as e:
                jsonFile.seek(0)
                errorLine = ""
                errorCol = 0
                pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                match = re.match(pattern, str(e))
                if match:
                    line_num = int(match.group(1))
                    for i,line in enumerate(jsonFile):
                        if i == (line_num - 1):
                            errorLine = line
                        if i > line_num:
                            break
                    errorCol = int(match.group(2))
                errors.append([
                    f"🔴ERROR: Schema '{schemaFilename}' is malformed!",
                    e,
                    errorLine.replace("\n",""),
                    ("-" * (errorCol - 3)) + "^"
                ])
                bail = True

print("VALIDATE")

# regions
print(" REGIONS")
room_validator = Draft7Validator(
    schema=schemas["z3oa"]["room"],
    resolver=RefResolver(
        base_uri=schemaURI,
        referrer=schemas["z3oa"]["room"]
    )
)
for region in os.listdir(os.path.join(".", "region")):
    if os.path.isdir(os.path.join(".", "region", region)):
        print("  " + region.capitalize())
        for subregion in os.listdir(os.path.join(".", "region", region)):
            if os.path.isdir(os.path.join(".", "region", region, subregion)):
                if "roomDiagrams" not in subregion:
                    print("   " + subregion)
                    for roomFileName in os.listdir(os.path.join(".", "region", region, subregion)):
                        if ".json" in roomFileName:
                            roomName = roomFileName.replace(".json", "")
                            with open(
                                os.path.join(
                                    ".",
                                    "region",
                                    region,
                                    subregion,
                                    roomFileName
                                ),
                                "r",
                                encoding="utf-8"
                            ) as jsonFile:
                                roomJSON = None
                                try:
                                    roomJSON = json.load(jsonFile)
                                except json.JSONDecodeError as e:
                                    jsonFile.seek(0)
                                    errorLine = ""
                                    errorCol = 0
                                    pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
                                    match = re.match(pattern, str(e))
                                    if match:
                                        line_num = int(match.group(1))
                                        for i,line in enumerate(jsonFile):
                                            if i == (line_num - 1):
                                                errorLine = line
                                            if i > line_num:
                                                break
                                        errorCol = int(match.group(2))
                                    errors.append([
                                        f"🔴ERROR: Room '{region}/{subregion}/{roomName}' is malformed!",
                                        e,
                                        errorLine.replace("\n",""),
                                        ("-" * (errorCol - 3)) + "^"
                                    ])
                                    bail = True


                                if roomJSON:
                                    try:
                                        result = room_validator.validate(roomJSON)
                                    except JSONSchemaExceptions.ValidationError as e:
                                        errors.append([
                                            f"🔴ERROR: Room '{region}/{subregion}/{roomName}' doesn't validate!",
                                            e,
                                            "---"
                                        ])
                                        bail = True

                                if result:
                                    print("    " + "INVALID")
                                    pass
print()

# root
for rootType in [
    "helpers",
    "items",
    # "tech"
]:
    print(" " + rootType.upper())
    filePath = os.path.join(".", rootType + ".json")
    print("  " + filePath)
    with open(filePath, "r", encoding="utf-8") as jsonFile:
        fileJSON = None

        try:
            fileJSON = json.load(jsonFile)
        except json.JSONDecodeError as e:
            jsonFile.seek(0)
            errorLine = ""
            errorCol = 0
            pattern = r"^(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)(\d+)(?:\D+)$"
            match = re.match(pattern, str(e))
            if match:
                line_num = int(match.group(1))
                for i,line in enumerate(jsonFile):
                    if i == (line_num - 1):
                        errorLine = line
                    if i > line_num:
                        break
                errorCol = int(match.group(2))
            errors.append([
                f"🔴ERROR: {rootType} data '{filePath}' is malformed!",
                e,
                errorLine.replace("\n",""),
                ("-" * (errorCol - 3)) + "^"
            ])
            bail = True

        if fileJSON:
            try:
                result = validate(
                    instance=fileJSON,
                    schema=schemas["z3oa"][rootType],
                    resolver=RefResolver(
                        base_uri=schemaURI,
                        referrer=schemas["z3oa"][rootType]
                    )
                )
            except JSONSchemaExceptions.ValidationError as e:
                errors.append([
                    f"🔴ERROR: {rootType} data '{filePath}' doesn't validate!",
                    e,
                    "---"
                ])
                bail = True

        if result:
            print("     " + "INVALID")
            pass
    print()

if bail:
    for errorSet in errors:
        for error in errorSet:
            print(error)
    print("🔴Something fucked up! Bailing!")
    exit(1)
