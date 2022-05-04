ifeq "$(and $(PROJECT_HOME), $(CI_REGISTRY))" ""
ifeq ("$(shell test -e config/.env && echo exist)","exist")
include config/.env
export $(shell sed 's/=.*//' config/.env)
else
$(info Coping "config/.env.example" to "config/.env".)
dummy := $(shell cp config/.env.example config/.env)
include config/.env
export $(shell sed 's/=.*//' config/.env)
endif
endif


TEST_CMD=python -m pytest tests --tb=short -vv
#/* --cov=$(PROJECT_HOME)
CHECK_CMD=sh -c "pre-commit run isort -a && \
			pre-commit run autopep8 -a && \
			pre-commit run flake8 -a && \
			pre-commit run mypy -a && \
			pre-commit run bandit -a && \
			pre-commit run xenon -a && \
			pre-commit run bandit && \
			pre-commit run yamllint -a"


af:
	isort $(PROJECT_HOME)
	autopep8 -a -a -a -i -r $(PROJECT_HOME)

check:
	$(CHECK_CMD)

test:
	$(TEST_CMD)

t:
	$(TEST_DEBUG_CMD)

run:
	$(RUN_CMD)

pip_upgrade:
	pip install --upgrade pip setuptools pip-tools

requirements.txt: requirements.in | pip_upgrade
	pip-compile --no-emit-index-url --no-emit-trusted-host

requirements-local.in:
	@if [ ! -f requirements-local.in ]; then \
		printf -- $(DEFAULT_LOCAL_REQS) > requirements-local.in; \
	fi

requirements-local.txt: requirements.txt requirements-local.in | pip_upgrade
	pip-compile --no-emit-index-url --no-emit-trusted-host requirements-local.in

pip-install: requirements.txt requirements-local.txt
	pip-sync requirements.txt requirements-local.txt

install: pip-install
	pre-commit install

clean: pip_upgrade
	pip uninstall -y -r <(pip freeze)
	rm requirements.txt


all: down build up test

build:
	docker-compose build

up:
	docker-compose up -d app

down:
	docker-compose down --remove-orphans

test1: up
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/unit /tests/integration /tests/e2e

unit-tests:
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/unit

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/integration

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest app /tests/e2e

logs:
	docker-compose logs app | tail -100
