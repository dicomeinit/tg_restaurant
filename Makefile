setup:
	./manage.py migrate
	./manage.py first_setup
	cp .env.example .env

format:
	isort .
	black .
	autoflake .