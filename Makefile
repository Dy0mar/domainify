PROJECT = domainify
ENV ?= env
HOST = localhost
PORT = 8000

PEP8 = $(ENV)/bin/flake8
PYLINT = $(ENV)/bin/pylint
PYTHON = $(ENV)/bin/python
PIP = $(ENV)/bin/pip

MANAGE = $(PYTHON) manage.py


env:
	virtualenv --system-site-packages $(ENV)

pep8:
	$(PEP8) --statistics $(PROJECT) apps --exclude=migrations,settings_local.py

pylint:
	$(PYLINT) --rcfile=pylint.rc --load-plugins pylint_django $(PROJECT)

reqs: env
	$(PIP) install -r requirements.txt
	$(MANAGE) migrate

run:
	$(MANAGE) runserver $(HOST):$(PORT)

migrate:
	$(MANAGE) migrate

celery:
	. $(ENV)/bin/activate ; \
	celery worker -A domainify --loglevel=info --concurrency=4 -B

shell:
	$(MANAGE) shell

