#!/bin/bash
set -e

echo "Starting application..."

if [ -n "${DATABASE_HOST}" ] && [ "${DATABASE_HOST}" != "localhost" ]; then
  echo "Waiting for database at ${DATABASE_HOST}:${DATABASE_PORT:-5432}..."
  
  timeout=30
  elapsed=0
  until nc -z "${DATABASE_HOST}" "${DATABASE_PORT:-5432}" || [ $elapsed -ge $timeout ]; do
    echo "Database is unavailable - sleeping"
    sleep 2
    elapsed=$((elapsed + 2))
  done
  
  if [ $elapsed -ge $timeout ]; then
    echo "Warning: Database connection timeout. Application will start but may not be fully functional."
  else
    echo "Database is up - initializing tables..."
    
    python -c "
from backend.app import create_app
from backend.app.config import create_tables
import sys

try:
    app = create_app()
    with app.app_context():
        create_tables()
    print('Tables created successfully')
except Exception as e:
    print(f'Warning: Could not create tables: {e}', file=sys.stderr)
    print('Application will attempt to create tables on first request', file=sys.stderr)
"
  fi
else
  echo "No external database configured, skipping database wait..."
fi

echo "Starting app..."
exec "$@"
