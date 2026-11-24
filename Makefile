base_command=docker compose run api

ruff:
	${base_command} uv run ruff check

fix:
	${base_command} uv run ruff check --fix

format:
	${base_command} uv run ruff format

up:
	docker compose up --watch

down:
	docker compose down
