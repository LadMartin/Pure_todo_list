# TODO list RestAPI

## Create and activate the venv
Create and activate your virtual env. using commands
`python3 -m venv myVenv`
`source ./myVenv/bin/activate`

## Instal all dependencies into your venv
For installation of all dependencies use the command `pip install -r requirements.txt`
For upgrade dependencies use the command `pip install --upgrade -r requirements.txt`

## Runn app
Run app from project root directory using the command `python3 app.py`
For the debug mode you can use the argumet for running the app `app.run(debug=True)`

## Run tests
Run tests from the project root directory using the command `py.test -vvs tests/tests_app.py`
For runing the concrete tests add the parameter `-k <test_name>`
