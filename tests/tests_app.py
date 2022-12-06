
from datetime import datetime, timedelta
import pytest
import requests

'''
Velka pochvala za testy ale priznam se ze jsem je necetl :D

nicmene co by stalo za zvazeni je jestli neudelat nejaky builder pro zamotne data
protoze ne vzdy chceme menit vsechno

def data_builder(id=TODO_ID, text='uklidit pokoj', deadline=DATE_NOW):
    return {
        "id": id,
        "text": text,
        "deadline": deadline,
    }

pripadne nejake slozitejsi variace

mozna i nejakou abstrakci nad url

def url(args):
    return f"{URL}/todo" + '/'.join(args)
'''


URL = "http://localhost:5000"
TODO_ID = "Ukol_1"
CONTENT_TYPE_JSON = {"content-type": "application/json"}
CONTENT_TYPE_HTML = {"content-type": "text/html"}
now = datetime.now()
DATE_NOW = now.strftime("%Y-%m-%d")
DATE_TOMORROW =  (now + timedelta(days=1)).strftime("%Y-%m-%d")
DATE_NEXT_WEEK = (now + timedelta(days=7)).strftime("%Y-%m-%d")
DATE_NEXT_MONTH = (now + timedelta(days=31)).strftime("%Y-%m-%d")
DATE_NEXT_YEAR = (now + timedelta(days=365)).strftime("%Y-%m-%d")


@pytest.fixture
def setup_cleanup():
    yield
    delete_todo_success(TODO_ID)


@pytest.fixture
def setup_create_cleanup():
    create_todo_success(TODO_ID, DATE_NOW)
    yield
    delete_todo_success(TODO_ID)


@pytest.fixture
def setup_data_filetrs():
    deadlines = [DATE_NOW, DATE_NEXT_MONTH, DATE_NEXT_WEEK, DATE_TOMORROW]
    for deadline in deadlines:
        create_todo_success(TODO_ID, deadline)
    yield
    delete_todo_success(TODO_ID)


def create_todo_success(TODO_ID, DATE_NOW):
    json_request = {
        "id": TODO_ID,
        "text": "Uklidit pokoj",
        "deadline": DATE_NOW,
        }
    response = requests.post(f"{URL}/todo", headers=CONTENT_TYPE_JSON, json=json_request)
    print(response.status_code)
    assert response.text == "Created"
    assert response.status_code == 201


def delete_todo_success(TODO_ID):
    response = requests.delete(f"{URL}/todo/{TODO_ID}")
    print(response.status_code)
    assert response.status_code == 204


def test_create_todo_success(setup_cleanup):
    create_todo_success(TODO_ID, DATE_NOW)
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    print(response.status_code)
    assert response.status_code == 200


def test_create_todo_duplicated_delete_both():
    create_todo_success(TODO_ID, DATE_NOW)
    create_todo_success(TODO_ID, DATE_NOW)
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        },
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200
    delete_todo_success(TODO_ID)
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == []
    assert response.status_code == 200


def test_get_todo_success(setup_create_cleanup):
    create_todo_success(TODO_ID, DATE_NOW)
    response = requests.get(f"{URL}/todo/{TODO_ID}")
    print(response.status_code)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        },
                {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todo_non_existing(setup_create_cleanup):
    response = requests.get(f"{URL}/todo/Ukol22")
    print(response.status_code)
    assert response.text == "ID not found"
    assert response.status_code == 404


def test_get_todo_duplicated_success(setup_create_cleanup):
    response = requests.get(f"{URL}/todo/{TODO_ID}")
    print(response.status_code)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todos_empty_success():
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    print(response.status_code)
    assert response.status_code == 200


def test_get_todos_data_success(setup_create_cleanup):
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_date_to_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_NOW}&date_to={DATE_NEXT_WEEK}", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        },
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NEXT_WEEK,
            "is_done": False
        },
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_TOMORROW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_date_to_empty(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_TOMORROW}&date_to={DATE_NOW}", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == []
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_today_count1_sort_by_urgency_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_NOW}&count=1&sort_by=urgency", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_now_count1_sort_by_id():
    create_todo_success("Ukol2", DATE_NOW)
    create_todo_success("Ukol1", DATE_NOW)
    response = requests.get(f"{URL}/todos?date_from={DATE_NOW}&count=1&sort_by=id", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": "Ukol1",
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200
    delete_todo_success("Ukol1")
    delete_todo_success("Ukol2")


def test_get_todos_data_filter_date_from_now_count2_sort_by_urgency_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_NOW}&count=2&sort_by=urgency", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        },
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_TOMORROW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_next_year_count1_sort_by_urgency_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_NEXT_YEAR}&count=1&sort_by=urgency", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == []
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_today_count0_sort_by_urgency_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_NOW}&count=0&sort_by=urgency", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == []
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_now_count1_sort_by_urgency_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from=now&count=1&sort_by=urgency", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_todos_data_filter_date_from_tomorrow_count4_sort_by_urgency_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_from={DATE_TOMORROW}&count=4&sort_by=urgency", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_TOMORROW,
            "is_done": False
        },
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NEXT_WEEK,
            "is_done": False
        },
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NEXT_MONTH,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_most_urgent_todo_success(setup_data_filetrs):
    response = requests.get(f"{URL}/most_urgent", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_get_most_urgent_todo_empty_success():
    response = requests.get(f"{URL}/most_urgent", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == []
    assert response.status_code == 200


def test_get_todos_data_filter_date_to_now_is_done_false_success(setup_data_filetrs):
    response = requests.get(f"{URL}/todos?date_to=now&is_done=False", headers=CONTENT_TYPE_JSON)
    print(response.json())
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_update_todo_set_done_success(setup_create_cleanup):
    response = requests.put(f"{URL}/{TODO_ID}/set_done")
    print(response.status_code)
    assert response.text == "Updated"
    assert response.status_code == 200
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": True
        }
    ]
    assert response.status_code == 200


def test_update_todo_set_done_invalid_status(setup_create_cleanup):
    response = requests.put(f"{URL}/{TODO_ID}/done")
    print(response.status_code)
    print(response.text)
    assert response.status_code == 400
    assert response.text == "Invalid"

    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_update_todo_set_done_invalid_id(setup_create_cleanup):
    response = requests.put(f"{URL}/Ukol!/set_done")
    print(response.status_code)
    print(response.text)
    assert response.status_code == 400
    assert response.text == "Invalid"
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_update_todo_set_not_done_success(setup_create_cleanup):
    response = requests.put(f"{URL}/{TODO_ID}/set_done")
    print(response.status_code)
    assert response.status_code == 200
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": True
        }
    ]
    assert response.status_code == 200
    response = requests.put(f"{URL}/{TODO_ID}/set_not_done")
    print(response.status_code)
    assert response.status_code == 200
    response = requests.get(f"{URL}/todos", headers=CONTENT_TYPE_JSON)
    assert response.json() == [
        {
            "id": TODO_ID,
            "text": "Uklidit pokoj",
            "deadline": DATE_NOW,
            "is_done": False
        }
    ]
    assert response.status_code == 200


def test_update_todo_not_found():
    response = requests.put(f"{URL}/Ukol_22/set_done")
    assert response.text == "ID not found"
    assert response.status_code == 404


def test_create_todo_method_not_allowed():
    json_request = {
        "id": TODO_ID,
        "text": "uklidit pokoj",
        "deadline": "2022-11-30"
        }
    response = requests.put(f"{URL}/todo", headers=CONTENT_TYPE_JSON, json=json_request)
    print(response.status_code)
    assert response.status_code == 405


def test_create_todo_invalid_headers():
    json_request = {
        "id": TODO_ID,
        "text": "uklidit pokoj",
        "deadline": "2022-11-30"
        }
    response = requests.post(f"{URL}/todo", json=json_request, headers=CONTENT_TYPE_HTML)
    print(response.status_code)
    assert response.text == "Content-Type not supported"
    assert response.status_code == 406


def test_get_todos_data_method_not_allowed(setup_create_cleanup):
    response = requests.delete(f"{URL}/todos")
    print(response.status_code)
    assert response.status_code == 405




def test_create_todo_validation():
    invalid_json_requests = {
       "id - invalid characters" :{
            "id": "Ukol_2+-*#&@.[]",
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "id - invalid white space": {
            "id": "Ukol 1",
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "id - invalid comma": {
            "id": "Ukol,",
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "id - invalid cz characters": {
            "id": "ěščřžýáíé",
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "id - invalid data type": {
            "id": True,
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "id - invalid empty string": {
            "id": "",
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "id - invalid missing field": {
            "text": "uklidit pokoj",
            "deadline": DATE_NOW
        },
        "text - invalid empty string": {
            "id": TODO_ID,
            "text": "",
            "deadline": DATE_NOW
        },
        "text - invalid data type": {
            "id": TODO_ID,
            "text": 1,
            "deadline": DATE_NOW
        },
        "text - invalid missing field": {
            "id": "Ukol_4",
            "deadline": DATE_NOW
        },
        "deadline - invalid empty string": {
            "id": TODO_ID,
            "text": "",
            "deadline": ""
        },
        "deadline - invalid date format": {
            "id": TODO_ID,
            "text": "uklidit pokoj",
            "deadline": "2022-11-300000"
        },
        "deadline - invalid date" : {
            "id": TODO_ID,
            "text": "uklidit pokoj",
            "deadline": "2022-33-33"
        },
        "deadline - invalid missing field": {
            "id": TODO_ID,
            "text": "uklidit pokoj"
        },
        "is_done - extra field": {
            "id": "Ukol_10",
            "text": "uklidit pokoj",
            "deadline": DATE_NOW,
            "extra": "extra"
        }
    }
    print("\nTested values:")
    for name, request in invalid_json_requests.items():
        response = requests.post(f"{URL}/todo", headers=CONTENT_TYPE_JSON, json=request)
        if response.status_code != 400:
            print(name, response.status_code)
        assert response.status_code == 400


def test_get_todos_filter_invalid_argument(setup_data_filetrs):
    invalid_contents = [
        f"{URL}/todos?date_from=2022-22-32&date_to={DATE_TOMORROW}&is_done=False&sort_by=deadline&count=2",
        f"{URL}/todos?date_from={DATE_NOW}&date_to=22-12-10&is_done=False&sort_by=deadline&count=2",
        f"{URL}/todos?date_from={DATE_NOW}&date_to={DATE_TOMORROW}&is_done=notdone&sort_by=deadline&count=2",
        f"{URL}/todos?date_from={DATE_NOW}&date_to={DATE_TOMORROW}&is_done=False&sort_by=time&count=2",
        f"{URL}/todos?date_from={DATE_NOW}&date_to={DATE_TOMORROW}&is_done=False&sort_by=deadline&count=two"
        f"{URL}/todos?date_from={DATE_NOW}&date_to={DATE_TOMORROW}&is_done=False&sort_by=deadline&count=2&is_done=not"
        f"{URL}/todos?date_from={DATE_NOW}&date_to={DATE_TOMORROW}&is_done=False&count=2&is_done=False&extra=extra"
    ]
    for content in invalid_contents:
        response = response = requests.get(content, headers=CONTENT_TYPE_JSON)
        if response.status_code != 400:
            print(content, response.status_code)
        assert response.status_code == 400


def test_update_todo_set_done_invalid_items(setup_create_cleanup):
    invalid_contents = [
        f"{URL}/1254!/set_done",
        f"{URL}/{TODO_ID}/done",
    ]
    for content in invalid_contents:
        response = response = requests.put(content)
        if response.status_code != 400:
            print(content, response.status_code)
        assert response.status_code == 400
