#!/bin/bash
set -e

if [ "${INITIALIZE_DB}" = "1" ]; then
  echo "Running database initialization..."
  python << 'EOF'
from fast_api_template.db import create_db_and_tables
import sqlalchemy.exc

try:
    create_db_and_tables()
except sqlalchemy.exc.OperationalError as e:
    print(f'Database already initialized: {e}')
EOF
fi

case "$1" in
  "api")
    echo "Starting FastAPI application..."
    exec uvicorn fast_api_template.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
    ;;
  "worker")
    echo "Starting worker..."
    exec python -m fast_api_template.worker
    ;;
  *)
    echo "Unknown command: $1"
    echo "Available commands: api, worker"
    exit 1
    ;;
esac
