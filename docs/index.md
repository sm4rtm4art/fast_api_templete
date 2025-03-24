# Fast API Template

A modern, production-ready FastAPI template with best practices for rapid development.

## Features

- **Modern Python**: Type hints, async support, and latest Python 3.12 features
- **Fast API Framework**: High performance, easy to learn, fast to code
- **Database Integration**: SQLModel with PostgreSQL for robust data handling
- **Authentication**: JWT token auth with role-based access control
- **Documentation**: Auto-generated API docs with Swagger/ReDoc
- **Testing**: Comprehensive test suite with pytest
- **Containerization**: Docker and Docker Compose configuration
- **CI/CD**: GitHub Actions workflows for testing and deployment
- **Dependency Management**: Uses UV for fast, deterministic dependency management
- **Security**: Built-in security features and vulnerability scanning
- **Monitoring**: Health checks and logging setup
- **Development Tools**: Pre-configured linting, formatting, and type checking

## Quick Start

```bash
# Clone the repository
git clone https://github.com/sm4rtm4art/FAST_API_TEMPLATE.git
cd FAST_API_TEMPLATE

# Install dependencies
curl -sSf https://install.determinate.systems/uv | sh -s -- --yes
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,lint,test]"

# Start development server with Docker
make docker-run

# Access the API documentation
open http://localhost:8000/docs
```

## Documentation

- [Project Structure](guide/project-structure.md) - Code organization and architecture
- [Development Guide](guide/development.md) - Setting up and running the project
- [API Documentation](guide/api.md) - API endpoints and usage
- [Database Guide](guide/database.md) - Database setup and migrations
- [Testing Guide](guide/testing.md) - Running and writing tests
- [CI/CD Guide](guide/ci-cd.md) - Continuous Integration and Deployment
- [Security Guide](guide/security.md) - Security features and best practices
- [Docker Guide](guide/docker.md) - Containerization and deployment

## Technologies

- [FastAPI](https://fastapi.tiangolo.com/): Modern, fast web framework
- [SQLModel](https://sqlmodel.tiangolo.com/): SQL databases in Python with type annotations
- [PostgreSQL](https://www.postgresql.org/): Powerful, open source object-relational database
- [UV](https://github.com/astral-sh/uv): Fast Python package installer and resolver
- [Docker](https://www.docker.com/): Containerization for consistent environments
- [GitHub Actions](https://github.com/features/actions): CI/CD workflows
- [Pydantic](https://docs.pydantic.dev/): Data validation using Python type annotations
- [SQLAlchemy](https://www.sqlalchemy.org/): SQL toolkit and ORM
- [Ruff](https://github.com/astral-sh/ruff): Fast Python linter and formatter
- [pytest](https://docs.pytest.org/): Testing framework
- [mypy](https://mypy.readthedocs.io/): Static type checker
- [Dynaconf](https://www.dynaconf.com/): Configuration management
- [Structlog](https://www.structlog.org/): Structured logging
- [Typer](https://typer.tiangolo.com/): CLI interface builder

## Contributing

See our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the terms of the MIT license - see the [LICENSE](LICENSE) file for details.
