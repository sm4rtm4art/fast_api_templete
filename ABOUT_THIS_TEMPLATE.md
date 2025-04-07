# About this template

Hi, I created this template to help you get started with a new project.

I have created and maintained a number of python libraries, applications and
frameworks and during those years I have learned a lot about how to create a
project structure and how to structure a project to be as modular and simple
as possible.

Some decisions I have made while creating this template are:

- Create a project structure that is as modular as possible.
- Keep it simple and easy to maintain.
- Allow for a lot of flexibility and customizability.
- Low dependency (this template doesn't add dependencies)

## Structure

Lets take a look at the structure of this template:

```text
├── Dockerfile               # Multi-stage Docker build for dev and production
├── CONTRIBUTING.md          # Onboarding instructions for new contributors
├── docs                     # Documentation site (add more .md files here)
│   └── index.md             # The index page for the docs site
├── .github                  # Github metadata for repository
│   ├── release_message.sh   # A script to generate a release message
│   └── workflows            # The CI pipeline for Github Actions
├── .gitignore               # A list of files to ignore when pushing to Github
├── HISTORY.md               # Auto generated list of changes to the project
├── LICENSE                  # The license for the project
├── Makefile                 # A collection of utilities to manage the project
├── MANIFEST.in              # A list of files to include in a package
├── mkdocs.yml               # Configuration for documentation site
├── fast_api_template        # The main python package for the project
│   ├── api/                 # API endpoints organized by version
│   ├── models/              # Data models (SQLModel, Pydantic)
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions and helpers
│   ├── __init__.py          # This tells Python that this is a package
│   ├── app.py               # The main FastAPI application
│   ├── config.py            # Configuration using Pydantic settings
│   └── VERSION              # The version for the project is kept in a static file
├── README.md                # The main readme for the project
├── pyproject.toml           # The pyproject.toml file for packaging and dependencies
├── docker-compose.yaml      # Docker Compose setup with profiles for dev/prod
├── .env.example             # Example environment variables file
└── tests                    # Unit tests for the project
    ├── conftest.py          # Configuration, hooks and fixtures for pytest
    ├── __init__.py          # This tells Python that this is a test package
    └── test_modules/        # Tests organized by module
```

## FAQ

Frequent asked questions.

### Why this template uses pyproject.toml instead of setup.py?

The template now uses `pyproject.toml` as this is the modern approach to Python packaging. PEP 517 and PEP 518 standardized this approach, making it easier to define build requirements and configuration in a single file.

Benefits of using pyproject.toml include:

- Unified configuration for build, dependencies, and development tools
- Better compatibility with modern packaging tools
- Cleaner project structure
- Standardized approach supported by pip and other package managers

### Why there is a Dockerfile instead of separate Dockerfile.dev and Dockerfile?

This template uses a multi-stage Dockerfile, which allows defining separate build stages for development and production in a single file. This approach has several advantages:

- Standardizes the environment between development and production
- Reuses common layers between environments
- Simplifies maintenance (only one file to update)
- Follows Docker best practices
- Works with docker-compose profiles for easy deployment

### How are environment variables managed?

The template uses a `.env` file approach with Pydantic Settings for type-safe configuration. This replaces the previous Dynaconf/TOML approach with a simpler, more standard method.

An `.env.example` file is provided with detailed documentation of all available settings.

### Why the `VERSION` is kept in a static plain text file?

I used to have my version inside my main module in a `__version__` variable, then
I had to do some tricks to read that version variable inside the setuptools
`setup.py` file because that would be available only after the installation.

I decided to keep the version in a static file because it is easier to read from
wherever I want without the need to install the package.

e.g: `cat fast_api_template/VERSION` will get the project version without harming
with module imports or anything else, it is useful for CI, logs and debugging.

### Why to include `tests`, `history` and `Dockerfile` as part of the release?

The `MANIFEST.in` file is used to include the files in the release, once the
project is released to PyPI all the files listed on MANIFEST.in will be included
even if the files are static or not related to Python.

Some build systems such as RPM, DEB, AUR for some Linux distributions, and also
internal repackaging systems tends to run the tests before the packaging is performed.

The Dockerfile can be useful to provide a safer execution environment for
the project when running on a testing environment.

I added those files to make it easier for packaging in different formats.

### Why conftest includes a go_to_tmpdir fixture?

When your project deals with file system operations, it is a good idea to use
a fixture to create a temporary directory and then remove it after the test.

Before executing each test pytest will create a temporary directory and will
change the working directory to that path and run the test.

So the test can create temporary artifacts isolated from other tests.

After the execution Pytest will remove the temporary directory.

## The Makefile

All the utilities for the template and project are on the Makefile

```bash
❯ make
Usage: make <target>

Targets:
help:             ## Show the help.
install:          ## Install the project in dev mode.
fmt:              ## Format code using black & isort.
lint:             ## Run pep8, black, mypy linters.
test: lint        ## Run tests and generate coverage report.
watch:            ## Run tests on every change.
clean:            ## Clean unused files.
virtualenv:       ## Create a virtual environment.
release:          ## Create a new tag for release.
docs:             ## Build the documentation.
docker-build:     ## Build docker images for development.
docker-run:       ## Run docker development environment with hot-reloading.
docker-stop:      ## Stop docker development environment.
docker-ps:        ## List running docker containers.
docker-logs:      ## Show development docker logs.
docker-prod:      ## Build and run production Docker image.
docker-prod-stop: ## Stop production docker environment.
```
