define USAGE
Tubee, the YouTube subscription dashboard

Commands:
	install      Install dependencies for local development
	build        Build docker images
	start        Start the application for development
	test         Run coverage unit tests
	shell        Enter interactive shell for debug
	db_migrate	 Create a new database migration (Run with make db_migrate MESSAGE="message")
	db_upgrade	 Upgrade the database to the latest migration
	uninstall    Uninstall environment
	reinstall    Reinstall environment (when Python version is bumped)

endef

export USAGE

help:
	@echo "$$USAGE"

install:
	pyenv install -s $(shell cat .python-version)
	poetry env use $(shell echo $(shell pyenv shell $(shell cat .python-version); pyenv which python))
	poetry install

build:
	docker compose --file docker-compose.dev.yml build

start:
	docker compose --file docker-compose.dev.yml up

test:
	poetry run flask test --coverage

shell:
	poetry run flask shell

db_migrate:
	docker compose --file docker-compose.dev.yml exec tubee flask db migrate -m $(MESSAGE)

db_upgrade:
	docker compose --file docker-compose.dev.yml exec tubee flask db upgrade

uninstall:
	poetry env remove --all

reinstall: uninstall install build
