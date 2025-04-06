.ONESHELL:
ENV_PREFIX=$(shell python -c "if __import__('pathlib').Path('.venv/bin/python').exists(): print('.venv/bin/')")

.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep

.PHONY: setup
setup:            ## Complete project setup (env, deps, pre-commit, db).
	@echo "Setting up project..."
	@make install
	@make pre-commit
	@make db-create
	@make db-migrate
	@echo "Setup complete! Run 'make docker-run' to start the application."

.PHONY: setup-dev
setup-dev:        ## Development environment setup with Docker.
	@echo "Setting up development environment..."
	@make docker-build
	@make docker-run
	@echo "Development environment ready! Access the API at http://localhost:8000"

.PHONY: pre-commit
pre-commit:       ## Install and setup pre-commit hooks.
	@echo "Setting up pre-commit hooks..."
	@$(ENV_PREFIX)pre-commit install
	@$(ENV_PREFIX)pre-commit autoupdate

.PHONY: db-create
db-create:        ## Create the database.
	@echo "Creating database..."
	@createdb fast_api_template || true

.PHONY: db-migrate
db-migrate:       ## Run database migrations.
	@echo "Running database migrations..."
	@$(ENV_PREFIX)sqlmodel migrate

.PHONY: db-reset
db-reset:         ## Reset the database (drop and recreate).
	@echo "Resetting database..."
	@dropdb fast_api_template || true
	@make db-create
	@make db-migrate

.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	@echo "Running using $(ENV_PREFIX)"
	@$(ENV_PREFIX)python -V
	@$(ENV_PREFIX)python -m site

.PHONY: install
install:          ## Install the project in dev mode.
	@echo "Installing project with UV..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "UV not found. Installing UV..."; \
		curl -sSf https://install.determinate.systems/uv | sh -s -- --yes; \
	fi
	@if [ ! -d ".venv" ]; then \
		uv venv; \
	fi
	$(ENV_PREFIX)uv pip install -e .[dev,lint,test,docs]

.PHONY: fmt
fmt:              ## Format code using ruff.
	$(ENV_PREFIX)ruff format fast_api_template/
	$(ENV_PREFIX)ruff format tests/

.PHONY: lint
lint:             ## Run ruff and mypy linters.
	$(ENV_PREFIX)ruff check fast_api_template/
	$(ENV_PREFIX)ruff check tests/
	$(ENV_PREFIX)mypy --ignore-missing-imports fast_api_template/

.PHONY: fix-lint
fix-lint:         ## Fix linting issues using ruff.
	$(ENV_PREFIX)ruff check --fix fast_api_template/
	$(ENV_PREFIX)ruff check --fix tests/

.PHONY: type-check
type-check:       ## Run type checker.
	$(ENV_PREFIX)mypy --ignore-missing-imports fast_api_template/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	$(ENV_PREFIX)pytest -v --cov-config .coveragerc --cov=fast_api_template -l --tb=short --maxfail=1 tests/
	$(ENV_PREFIX)coverage xml
	$(ENV_PREFIX)coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr $(ENV_PREFIX)pytest --picked=first -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf .ruff_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	@echo "Creating virtualenv with UV..."
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "UV not found. Installing UV..."; \
		curl -sSf https://install.determinate.systems/uv | sh -s -- --yes; \
	fi
	@rm -rf .venv
	@uv venv
	@./.venv/bin/uv pip install -e .[dev,lint,test,docs]
	@echo
	@echo "!!! Please run 'source .venv/bin/activate' to enable the environment !!!"

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@echo "$${TAG}" > fast_api_template/VERSION
	@$(ENV_PREFIX)gitchangelog > HISTORY.md
	@git add fast_api_template/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@$(ENV_PREFIX)mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL  || open $$URL

.PHONY: init
init:             ## Initialize the project based on an application template.
	@./.github/init.sh

.PHONY: shell
shell:            ## Open a shell in the project.
	@./.venv/bin/ipython -c "from fast_api_template import *"

.PHONY: docker-build
docker-build:	  ## Build docker images
	@docker compose -f docker-compose-dev.yaml -p fast_api_template build

.PHONY: docker-run
docker-run:  	  ## Run docker development images
	@docker compose -f docker-compose-dev.yaml -p fast_api_template up -d

.PHONY: docker-stop
docker-stop: 	  ## Bring down docker dev environment
	@docker compose -f docker-compose-dev.yaml -p fast_api_template down

.PHONY: docker-ps
docker-ps: 	  ## List docker containers
	@docker compose -f docker-compose-dev.yaml -p fast_api_template ps

.PHONY: docker-logs
docker-logs: 	  ## Show docker logs
	@docker compose -f docker-compose-dev.yaml -p fast_api_template logs -f app

.PHONY: docker-prod-build
docker-prod-build:	## Build production docker images
	@docker compose -f docker-compose.yaml -p fast_api_template_prod build

.PHONY: docker-prod-run
docker-prod-run:  	## Run production docker images
	@docker compose -f docker-compose.yaml -p fast_api_template_prod up -d

.PHONY: docker-prod-stop
docker-prod-stop: 	## Bring down production docker environment
	@docker compose -f docker-compose.yaml -p fast_api_template_prod down

.PHONY: mypy
mypy: ## Run mypy
	@echo "Running mypy..."
	@uv pip install tomli || echo "tomli already installed"
	$(ENV_PREFIX)mypy --config-file=pyproject.toml fast_api_template/

.PHONY: mypy-report
mypy-report: ## Run mypy with HTML report
	$(ENV_PREFIX)mypy --config-file=pyproject.toml --html-report ./mypy_html fast_api_template/

# This project has been generated from sm4rtm4rt/fastapi-project-template
# __author__ = 'Martin'
# __repo__ = https://github.com/sm4rtm4art/fast_api_templete
# __origin__ = https://github.com/rochacbruno/fastapi-project-template
