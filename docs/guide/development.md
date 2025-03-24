# Development Guide

This guide covers setting up and running the Fast API Template project for development.

## Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose
- Git
- UV (Python package installer)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sm4rtm4art/FAST_API_TEMPLATE.git
cd FAST_API_TEMPLATE
```

### 2. Install UV

```bash
curl -sSf https://install.determinate.systems/uv | sh -s -- --yes
```

### 3. Set Up Python Environment

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows

# Install dependencies
uv pip install -e ".[dev,lint,test]"
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fast_api_template

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_PREFIX=/api/v1
```

## Running the Application

### Using Docker (Recommended)

```bash
# Start all services
make docker-run

# Stop all services
make docker-stop

# View logs
make docker-logs
```

### Without Docker

```bash
# Start the development server
uvicorn fast_api_template.app:app --reload --port 8000
```

## Development Tools

### Code Formatting and Linting

```bash
# Format and lint code
make lint

# Fix formatting and linting issues
make fix-lint
```

### Type Checking

```bash
# Run type checker
make type-check
```

### Testing

```bash
# Run tests
make test

# Run tests with coverage
make test-cov
```

## Database Management

### Create Database

```bash
# Using Docker
make db-create

# Without Docker
createdb fast_api_template
```

### Run Migrations

```bash
# Using Docker
make db-migrate

# Without Docker
sqlmodel migrate
```

### Create Migration

```bash
# Create a new migration
make db-migration name=migration_name
```

## API Documentation

Once the application is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Health Checks

The application includes health check endpoints:

- `/health`: Basic health check
- `/health/db`: Database health check
- `/health/cache`: Cache health check (if configured)

## Debugging

### Using VS Code

1. Install the Python extension
2. Create a `.vscode/launch.json` file:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["fast_api_template.app:app", "--reload", "--port", "8000"],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

### Using PyCharm

1. Create a new Run Configuration
2. Set the script path to: `uvicorn`
3. Set the script parameters to: `fast_api_template.app:app --reload --port 8000`

## Common Issues

### Database Connection Issues

If you can't connect to the database:

1. Check if PostgreSQL is running
2. Verify database credentials in `.env`
3. Ensure the database exists
4. Check if migrations are up to date

### Port Conflicts

If port 8000 is already in use:

1. Find the process using the port:
   ```bash
   lsof -i :8000
   ```
2. Kill the process or use a different port:
   ```bash
   uvicorn fast_api_template.app:app --reload --port 8001
   ```

### Dependency Issues

If you encounter dependency conflicts:

1. Delete the virtual environment:
   ```bash
   rm -rf .venv
   ```
2. Recreate it and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e ".[dev,lint,test]"
   ```
