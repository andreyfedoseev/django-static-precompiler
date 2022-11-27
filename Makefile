all:
	docker-compose build

shell:
	docker-compose run --rm app /bin/bash

test:
	docker-compose run --rm app tox

mypy:
	docker-compose run --rm app mypy --strict ./src

package:
	rm -rf ./dist
	python3 -m build

test-publish: package
	twine upload --repository testpypi dist/*

publish: package
	twine upload dist/*

pre-commit:
	pre-commit run -a
