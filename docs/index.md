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

## Project Structure

This template follows a structured approach to organize code for maintainability and scalability. See [Project Structure](PROJECT_STRUCTURE.md) for details.

## Technologies

- [FastAPI](https://fastapi.tiangolo.com/): Modern, fast web framework
- [SQLModel](https://sqlmodel.tiangolo.com/): SQL databases in Python with type annotations
- [PostgreSQL](https://www.postgresql.org/): Powerful, open source object-relational database
- [UV](https://github.com/astral-sh/uv): Fast Python package installer and resolver
- [Docker](https://www.docker.com/): Containerization for consistent environments
- [GitHub Actions](https://github.com/features/actions): CI/CD workflows

## License

This project is licensed under the terms of the MIT license.
