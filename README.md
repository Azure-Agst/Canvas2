# Canvas 2.0

## Setup

- Clone the repo to your location of choice.
- Create a venv using `python3 -m venv .venv`
- Activate the venv using `source .venv/bin/activate`
  - Pro Tip: you can use the `.` shorthand for `source` in some shells
- Install requirements using `pip3 install -r requirements.txt`
- Make sure `.flaskenv` is up to date :)

-----

## Running

### Development

- Put all env vars in `.flaskenv` then use `flask run`.
  - Flask will load the variables in `.flaskenv` into the session, then launch the generator function in our package's `__init__.py` file

### Production

- `waitress-serve --call 'canvas2:create_app'`
  - Waitress does NOT use `.flaskenv`, but then again all variables that would have been specified in that file should be configured server-side anyway.

-----

## Testing

- Install the `canvas2` package in development mode using `pip3 install -e .`
  - This is the purpose of the `setup.py` file
  - `setup.cfg` is used later in our testing suite to specify vars for pytest and coverage.
- You are now ready to test!
- Then use `pytest` to test the code
  - Pytest will look for any files in `tests/` that begin with `test_`, and then run functions in those files that also begin with that same prefix.
- You can also run coverage tests with `coverage run -m pytest`
  - After running, generate a report using `coverage report`

-----

## References

Flask Tutorial: https://flask.palletsprojects.com/en/2.0.x/tutorial/
