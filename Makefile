all:
	docker compose build

update-dependencies:
	docker compose run --rm app poetry update

shell:
	docker compose run --rm app /bin/bash

test:
	docker compose run --rm app tox -p auto

check-types:
	docker compose run --rm app pyright

package:
	rm -rf ./dist
	poetry build

test-publish: package
	poetry publish -r testpypi

publish: package
	poetry publish

pre-commit:
	pre-commit run -a
