# Modern FastAPI Template

[![CI](https://github.com/sm4rtm4art/FAST_API_TEMPLATE/actions/workflows/main.yml/badge.svg)](https://github.com/sm4rtm4art/FAST_API_TEMPLATE/actions/workflows/main.yml)

A modern FastAPI project template featuring:

- 🚀 [FastAPI](https://fastapi.tiangolo.com/) - Modern, high-performance web framework
- 📦 [UV Package Manager](https://github.com/astral-sh/uv) - Ultra-fast Python package manager and resolver
- 🔍 [Ruff](https://docs.astral.sh/ruff/) - Extremely fast Python linter and formatter, written in Rust
- 🔒 [SQLModel](https://sqlmodel.tiangolo.com/) - Type-annotated ORM based on Pydantic and SQLAlchemy
- 🛠️ [Typer](https://typer.tiangolo.com/) - Build CLI applications with ease
- 🔐 [JWT Authentication](https://jwt.io/) - Secure token-based authentication
- 🧩 Interactive shell for development and debugging
- 🐳 Multi-stage Docker builds for optimized containers
- 📊 Comprehensive CI/CD with GitHub Actions
- 🌐 Cross-platform support (Windows, macOS, Linux)

_This template is a modernized fork of [rochacbruno/fastapi-project-template](https://github.com/rochacbruno/fastapi-project-template), optimized for Python 3.12+ and featuring state-of-the-art tooling._

## Features

- **Modern Package Management**: Uses UV instead of pip for 10-100x faster dependency resolution
- **Enhanced Linting**: Ruff replaces multiple tools (flake8, black, isort) with a single, faster solution
- **Type Safety**: Comprehensive type annotations and validation with mypy
- **Security Scanning**: Automated vulnerability scanning in dependencies
- **Container Optimization**: Multi-stage Docker builds for smaller, more secure images
- **GitHub Actions**: CI/CD pipeline that tests on all major platforms
- **Developer Experience**: Streamlined workflow with makefile commands and pre-commit hooks

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose (optional, for containerized development)
- PostgreSQL (for local development)

### Installation

```bash
# Clone the repository
git clone https://github.com/sm4rtm4art/FAST_API_TEMPLATE fast_api_template
cd fast_api_template

# Complete setup (recommended for new developers)
make setup

# Or set up development environment with Docker
make setup-dev
```

### Development Commands

```bash
# Show all available commands
make help

# Format code
make fmt

# Check code quality
make lint
make fix-lint  # Automatically fix linting issues
make type-check  # Run type checker

# Run tests
make test
make watch  # Run tests on file changes

# Database operations
make db-create    # Create database
make db-migrate   # Run migrations
make db-reset     # Reset database

# Docker commands
make docker-build     # Build development images
make docker-run       # Start development environment
make docker-stop      # Stop development environment
make docker-logs      # View application logs
make docker-ps        # List running containers

# Documentation
make docs             # Build and view documentation
```

## Project Structure

```
/
├── fast_api_template/      # Main application package
│   ├── models/             # SQLModel definitions
│   ├── routes/             # API endpoints
│   ├── app.py              # FastAPI application setup
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   └── security.py         # Authentication and authorization
├── tests/                  # Test suite
├── scripts/                # Utility scripts for development
├── .github/workflows/      # GitHub Actions CI/CD
├── docs/                   # Documentation
├── notebooks/              # Jupyter notebooks for exploration
├── pyproject.toml          # Project metadata and dependencies
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
└── Makefile                # Development commands
```

## Development

### Environment Setup

The project provides several setup options:

1. **Complete Setup** (recommended for new developers):

   ```bash
   make setup
   ```

   This will:

   - Install all dependencies
   - Set up pre-commit hooks
   - Create the database
   - Run migrations

2. **Docker Development Setup**:

   ```bash
   make setup-dev
   ```

   This will:

   - Build Docker images
   - Start the development environment

3. **Individual Setup Steps**:
   ```bash
   make install      # Install dependencies
   make pre-commit   # Set up pre-commit hooks
   make db-create    # Create database
   make db-migrate   # Run migrations
   ```

### Code Quality Tools

```bash
# Format code
make fmt

# Check code quality
make lint
make fix-lint  # Automatically fix issues
make type-check  # Run type checker

# Run tests
make test
make watch  # Run tests on file changes
```

### Configuration

This project uses [Dynaconf](https://dynaconf.com) for flexible configuration:

```python
from fast_api_template.config import settings

# Access configuration values
database_url = settings.db.uri
secret_key = settings.security.secret_key
```

Configuration can be provided via:

- Configuration files (settings.toml, .secrets.toml)
- Environment variables
- Command line arguments

## API Documentation

When running the application, API documentation is available at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## CI/CD Security Scanning

This template includes [Safety](https://safetycli.com/) for vulnerability scanning in the GitHub Actions workflow.

### Setting Up Safety API Key

1. Sign up for a free account at [https://safetycli.com/](https://safetycli.com/)
2. Get your API key from the Safety dashboard
3. Add the API key as a GitHub secret:
   - Go to your GitHub repository
   - Click "Settings" > "Secrets and variables" > "Actions"
   - Click "New repository secret"
   - Name: `SAFETY_API_KEY`
   - Value: Your Safety API key
   - Click "Add secret"

### Disabling Safety Scanning

If you don't want to use Safety scanning in your CI pipeline, you can:

**Option 1: Remove the safety step entirely**
Edit the file `.github/workflows/main.yml` and remove the safety scanning step:

```yaml
# Delete or comment out this section
- name: Check dependencies with safety
  env:
    SAFETY_API_KEY: ${{ secrets.SAFETY_API_KEY }}
  run: |
    source .venv/bin/activate
    safety scan
```

**Option 2: Make the safety step always pass**
Edit the file `.github/workflows/main.yml` and modify the safety scanning step to always exit with code 0:

```yaml
- name: Check dependencies with safety
  run: |
    source .venv/bin/activate
    safety scan || true  # The '|| true' makes the step always pass
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Acknowledgements

This project is a modernized version of [fastapi-project-template](https://github.com/rochacbruno/fastapi-project-template) by Bruno Rocha. It has been significantly enhanced with:

- UV package manager instead of pip/poetry
- Ruff linting and formatting instead of flake8/black/isort
- Multi-stage Docker builds for production
- Enhanced GitHub Actions workflows
- Cross-platform testing and compatibility
- Improved security scanning

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
