# Variables
COMPOSE_FILE := docker-compose.yml
DOCKER_COMPOSE := docker-compose -f $(COMPOSE_FILE)

APP_CONTAINER := django
DB_CONTAINER := postgres

# Docker commands
.PHONY: build up down stop restart logs ps

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down -v

stop:
	$(DOCKER_COMPOSE) stop

restart:
	$(DOCKER_COMPOSE) down -v && $(DOCKER_COMPOSE) up -d

logs:
	$(DOCKER_COMPOSE) logs -f

ps:
	$(DOCKER_COMPOSE) ps

# Django management commands
.PHONY: makemigrations migrate createsuperuser shell collectstatic

makemigrations:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) python manage.py makemigrations

migrate:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) python manage.py migrate

createsuperuser:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) python manage.py createsuperuser

shell:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) python manage.py shell

collectstatic:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) python manage.py collectstatic --noinput

# Testing and linting
.PHONY: test lint flake8 black

test:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) poetry run python manage.py test

lint: flake8 black

flake8:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) poetry run flake8 .

black:
	$(DOCKER_COMPOSE) exec $(APP_CONTAINER) poetry run black --check .

# Database commands
.PHONY: db-dump db-restore

db-dump:
	$(DOCKER_COMPOSE) exec $(DB_CONTAINER) pg_dump -U $$POSTGRES_USER $$POSTGRES_DB > db_dump.sql

db-restore:
	$(DOCKER_COMPOSE) exec -T $(DB_CONTAINER) psql -U $$POSTGRES_USER $$POSTGRES_DB < db_dump.sql
