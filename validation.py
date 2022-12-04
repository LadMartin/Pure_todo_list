
from datetime import datetime
from jsonschema import validate, exceptions


PATTERN_ID = "^[a-zA-Z0-9_]+$"
PATTERN_COUNT = "^[0-9]+$"
DATE_NOW = datetime.now().strftime("%Y-%m-%d")


def is_valid_datetime(value_str) -> bool:
    """check the validity of the date"""
    try:
        datetime.strptime(value_str, "%Y-%m-%d")
    except ValueError as err:
        print(err)
        return False
    return True


def validate_json(json_instance) -> bool:
    """validation of the JSON request with respect to the validation schema:
      1) "id" - a string containing characters a-z, A-Z, 0-9 and the underscore only,
      2) "deadline" - a string formatted as rrrr-mm-dd,
      4) "id", "text", "deadline", "is_done" are mandatory params,
      5) no additional fields are allowed"""

    schema_create_todo = {
        "type": "object",
        "properties": {
            "id": {
                "type":  "string",
                "pattern": PATTERN_ID
            },
            "text": {
                "type":  "string",
                "minLength": 1
            },
            "deadline":{
                "type":  "string",
                "minLength": 10,
                "maxLength": 10
            }
        },
        "required": ["id", "text", "deadline"],
        "additionalProperties": False
    }

    try:
        validate(instance=json_instance, schema=schema_create_todo)
    except exceptions.ValidationError as err:
        print(str(err))
        return False

    return is_valid_datetime(json_instance["deadline"])


def is_valid(items_dict) -> bool:
    """schema for validation of url items and arguments"""
    schema_items = {
        "type": "object",
        "properties": {
            "id": {
                "type":  "string",
                "pattern": PATTERN_ID
            },
            "status": {
                "enum": ["set_done", "set_not_done"]
            },
            "date_from":{
                "type":  "string",
                "minLength": 10,
                "maxLength": 10
            },
            "date_to":{
                "type":  "string",
                "minLength": 10,
                "maxLength": 10
            },
            "count": {
                "type":  ["integer", "string"],
                "pattern": PATTERN_COUNT
            },
            "sort_by": {
                "enum": ["id", "deadline", "text", "is_done", "urgency"]
            },
            "is_done": {
                "type": ["boolean", "string"],
                "enum": ["False", "True", "false", "true"]
            }
        },
        "additionalProperties": False
    }


    if "date_from" in items_dict.keys():
        items_dict["date_from"] = DATE_NOW if items_dict["date_from"] == "now" else items_dict["date_from"]
    if "date_to" in items_dict.keys():
        items_dict["date_to"] = DATE_NOW if items_dict["date_to"] == "now" else items_dict["date_to"]

    try:
        validate(instance=items_dict, schema=schema_items)
    except exceptions.ValidationError as err:
        print(str(err))
        return False

    items_date = ["date_from", "date_to", "deadline"]

    for date in items_date:
        if date in items_dict.keys():
            return is_valid_datetime(items_dict[date])

    return True
  