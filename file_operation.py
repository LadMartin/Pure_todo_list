import os
import json
from typing import List, Dict
from operator import itemgetter
import validation


PATH_TO_FILE = "./data_files/todos_data_file.JSON"


def apply_date_from_filter(input_list, date_from) -> List[Dict]:
    """return a list containing items with a date greater than the parameter date_from"""
    date_from = validation.DATE_NOW if date_from == "now" else date_from
    output_list = []
    for item_dict in range(len(input_list)):
        if date_from <= input_list[item_dict]["deadline"]:
            output_list.append(input_list[item_dict])
    return output_list


def apply_date_to_filter(input_list, date_to) -> List[Dict]:
    """return a list containing items with a date less or equal than the parameter date_to"""
    date_to = validation.DATE_NOW if date_to == "now" else date_to
    output_list = []
    for item_dict in range(len(input_list)):
        if input_list[item_dict]["deadline"] <= date_to:
            output_list.append(input_list[item_dict])
    return output_list


def apply_sort_by_urgency_filter(input_list, sort_by) -> List[Dict]:
    """return a list containing items sorted by date asc"""
    key = "deadline" if sort_by == "urgency" else sort_by
    output_list = sorted(input_list, key=itemgetter(key))
    return output_list


def apply_is_done_filter(input_list, status) -> List[Dict]:
    """return a list containing items with the given status"""
    output_list = []
    for item_dict in range(len(input_list)):
        if str(status) == str(input_list[item_dict]["is_done"]):
            output_list.append(input_list[item_dict])
    # predchozi zapis jde udelat na jeden radek, je veci nazoru jestli je to lepsi v tomhle pripade
    # ale v pythonu se to casto pouziva
    # [input_list[item_dict] for item_dict in range(len(input_list) if str(status) == str(input_list[item_dict]["is_done"])]
    return output_list


def apply_count_filter(input_list, count) -> List[Dict]:
    """return a list containing the requested number of items"""
    output_list = []

    '''
    l = [1,2,3,4]

    print(l[:7])
    toto je v poradku, neni potreba kontrola
    '''
    if count >= len(input_list):
        output_list = input_list

    output_list = input_list[:count]
    return output_list


def execute_query(args_dict) -> List[Dict]:
    """return a list containing the requested items"""
    with open(PATH_TO_FILE, mode='r', encoding="utf-8") as file:
        reader = json.loads(file.read())

    if args_dict:
        if ("date_from" in args_dict.keys() and reader):
            reader = apply_date_from_filter(reader, args_dict["date_from"])

        if ("date_to"in args_dict.keys() and reader):
            reader = apply_date_to_filter(reader, args_dict["date_to"])

        if ("sort_by" in args_dict.keys() and reader):
            reader = apply_sort_by_urgency_filter(reader, args_dict["sort_by"])

        if ("is_done" in args_dict.keys() and reader):
            reader = apply_is_done_filter(reader, args_dict["is_done"])

        if ("count" in args_dict.keys() and reader):
            reader = apply_count_filter(reader, int(args_dict["count"]))

    return json.dumps(reader)


def add_item_to_file(item_dict) -> bool:
    """add the requested item to the file"""
    content = []
    item_dict["is_done"] = False

    # toho bychom mohli delat nekde na zacatku programu v inicializaci a ne pri kazdem volani
    # asi by se nam mohlo stat ze nam nejaky zloduch file v prubehu programu smaze ale pak mame vetsi problem
    # protoze jsme prisli o vsechna data
    if not os.path.isfile(PATH_TO_FILE):
        with open(PATH_TO_FILE, mode='w', encoding='utf-8') as file:
            json.dump(content, file)

    with open(PATH_TO_FILE, mode="r", encoding="utf-8") as file:
        reader = json.load(file)

    reader.append(item_dict)

    with open(PATH_TO_FILE, mode='w', encoding='utf-8') as file:
        json.dump(reader, file)

    return True


def delete_item_from_file(item_id) -> bool:
    """delete the requested item from the file"""
    with open(PATH_TO_FILE, mode="r", encoding="utf-8") as file:
        reader = json.load(file)

    item_existence = False
    if reader:
        for item_dict in reversed(range(len(reader))):
            if reader[item_dict]["id"] == item_id:
                del reader[item_dict]
                item_existence = True

    if item_existence:
        with open(PATH_TO_FILE, mode='w', encoding='utf-8') as file:
            json.dump(reader, file)
        return True

    return False


def get_item_from_file(item_id) -> List[Dict]:
    """return the requested item from the file"""
    with open(PATH_TO_FILE, mode="r", encoding="utf-8") as file:
        reader = json.load(file)

    output_list = []
    if reader:
        for item_dict in range(len(reader)):
            if reader[item_dict]["id"] == item_id:
                output_list.append(reader[item_dict])

    return output_list


def update_item_in_file(item_id, status) -> bool:
    """update the status of the requested item in the file"""
    # Lze si vsimnout ze tento pattern se stale opakuje precist - upravit - zapsat
    # je to v update, delete, add
    # je dobre takovou to duplicaci redukovat
    status_value = True if status == "set_done" else False
    with open(PATH_TO_FILE, mode="r", encoding="utf-8") as file:
        reader = json.load(file)


    item_existence = False
    if reader:
        for item_dict in range(len(reader)):
            if reader[item_dict]["id"] == item_id:
                reader[item_dict]["is_done"] = status_value
                item_existence = True

    if item_existence:
        with open(PATH_TO_FILE, mode='w', encoding='utf-8') as file:
            json.dump(reader, file)
    

    return item_existence
