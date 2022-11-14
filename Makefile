all:
	docker-compose build

shell:
	docker-compose run --rm app /bin/bash

test:
	docker-compose run --rm app tox

package:
	rm -rf ./dist
	python3 -m build

test-publish: package
	twine upload --repository testpypi dist/*

publish: package
	twine upload dist/*

check-flake8:
	docker-compose run --rm app flake8

check-black:
	docker-compose run --rm app black --check ./static_precompiler

apply-black:
	docker-compose run --rm app black ./static_precompiler

check-isort:
	docker-compose run --rm app isort --check ./static_precompiler

apply-isort:
	docker-compose run --rm app isort ./static_precompiler
