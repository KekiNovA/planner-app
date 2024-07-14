# Planner App

This drf-based app is used to get weather forecast and nearby point of interests.

## Installation (For local)

Clone the repository and follow the setups.

```bash
  cd planner-app
  python -m venv venv
```

Activate venv

```bash
  source ./venv/bin/activate #For Linux
  myenv\Scripts\activate #For Windows
```

Install Requirements

```bash
  pip install -r requirements.txt
```

Once done, start by running the migrations

```bash
  python manage.py migrate
```

You can create superuser (admin), just follow along the prompted steps -

```bash
  python manage.py createsuperuser
```

Done now you can start the server and test the apis on localhost:8000

```bash
  python manage.py runserver
```

## Documentation

For Documentation of apis you can visit localhost:8000/swagger or localhost:8000/redoc.
Have also included doctrings.

## Running Tests

To run tests, run the following command

```bash
  python manage.py test
```
