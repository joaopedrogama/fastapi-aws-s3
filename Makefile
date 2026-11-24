base_ruff_command=docker compose run --rm -it -v ./app:/app/app api

ruff:
	${base_ruff_command} uv run ruff check

fix:
	${base_ruff_command} uv run ruff check --fix

format:
	${base_ruff_command} uv run ruff format

up:
	docker compose up --watch

down:
	docker compose down

build:
	docker compose build

rebuild:
	docker compose down -v --remove-orphans
	docker compose build --no-cache

