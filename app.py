
from flask import Flask, request
import validation
import file_operation

'''
Obecna slova:
plusy:
    stuktura kodu - rozdeleni do filu
    validace pres schema
    readme
    testy
minusy:
    opakujici se kod

myslim, ze by stalo za to i se zamyslet nad nejakym vice generickym pristupek k vraceni erroru.
v pythonu neni az zase takovy hrich zahrnout vyjimky jako soucast logiky takze klidne funkce misto vraceni false pri erroru mohou
raisnout vyjimku s konkretnejsim textem a mozna rovnou i kodem?
'''

app = Flask(__name__)

# jen navrh ze lze odchytavat vyjimky jako nejakou posledni zachranu aby nespadnul program
@app.errorhandler(ValueError)       
def basic_error(err):      
        print(err)
        return "Decoding JSON failed", 500


@app.route('/todos')
def get_all_todos():
    """get all requested todo entries"""
    args_dict = request.args.to_dict()
    if not validation.is_valid(args_dict):
        return "Data not valid", 400
    else:
        return file_operation.execute_query(args_dict), 200

@app.route('/most_urgent')
def most_urgent():
    """get the most urgent todo entry"""
    args_dict = {"date_from": "now", "count": "1", "sort_by": "urgency"}
    return file_operation.execute_query(args_dict), 200


@app.route('/todo', methods=['POST'])
def add_todo():
    """add a new todo entry"""
    if request.headers.get('Content-Type') != 'application/json':
        return "Content-Type not supported", 406
    try:
        request_json = request.json
    except ValueError as err:
        print(err)
        return "Invalid JSON format", 400

    if not validation.validate_json(request_json):
        return "Data not valid", 400
    if file_operation.add_item_to_file(request_json):
        return "Created", 201

@app.route('/todo/<todo_id>', methods=['DELETE', 'GET'])
def delete_todo(todo_id):
    """delete an existing todo entry for the given id (DELETE method) or return
    a list of todo entries for the givben todo id (GET method)"""
    if request.method == 'DELETE':
        if validation.is_valid({"id": todo_id}):
            if file_operation.delete_item_from_file(todo_id):
                return "Deleted", 204
            else:
                  return "ID not found", 404
        else:
              return "ID is invalid", 400
    else:
        if validation.is_valid({"id": todo_id}):
            result = file_operation.get_item_from_file(todo_id)
            if not result:
                return "ID not found", 404
            else:
                return result
        else:
            return "ID is invalid", 400



@app.route('/<todo_id>/<status>', methods=['PUT'])
def update_todo(todo_id, status):
    """update the status of the required todo entry"""
    if validation.is_valid({"id": todo_id, "status": status}):
        if file_operation.update_item_in_file(todo_id, status):
            return "Updated", 200
        else:
            return "ID not found", 404
    else:
        return "Invalid", 400



if __name__ == "__main__":
    app.run()
