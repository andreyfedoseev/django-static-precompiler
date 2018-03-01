all:
	docker-compose build

shell:
	docker-compose run --rm app /bin/bash

flake8:
	docker-compose run --rm app flake8

test:
	docker-compose run --rm app tox

upload:
	python setup.py sdist upload
