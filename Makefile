all:
	docker compose build

shell:
	docker compose run --rm app /bin/bash

test:
	docker compose run --rm app tox -p auto

mypy:
	docker compose run --rm app mypy --strict ./src

package:
	rm -rf ./dist
	poetry build

test-publish: package
	poetry publish -r testpypi

publish: package
	poetry publish

pre-commit:
	pre-commit run -a
