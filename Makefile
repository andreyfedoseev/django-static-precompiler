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

check-black:
	docker-compose run --rm app black --check ./static_precompiler

apply-black:
	docker-compose run --rm app black ./static_precompiler

check-isort:
	docker-compose run --rm app isort --check ./static_precompiler

apply-isort:
	docker-compose run --rm app isort ./static_precompiler
