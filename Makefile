PROJECT = turbo
ENV ?= env
HOST = localhost
PORT = 8000

PEP8 = $(ENV)/bin/flake8
PYLINT = $(ENV)/bin/pylint
PYTHON = $(ENV)/bin/python
PIP = $(ENV)/bin/pip

MANAGE = $(PYTHON) manage.py

GRUNT = ./node_modules/.bin/grunt


env:
	virtualenv --system-site-packages $(ENV)

pep8:
	$(PEP8) --statistics $(PROJECT) apps --exclude=migrations,settings_local.py

pylint:
	$(PYLINT) --rcfile=pylint.rc --load-plugins pylint_django turbo

reqs: env
	$(PIP) install -r requirements.txt
	$(MANAGE) migrate

run:
	$(MANAGE) runserver $(HOST):$(PORT)

migrate:
	$(MANAGE) migrate

grunt:
	$(GRUNT)
