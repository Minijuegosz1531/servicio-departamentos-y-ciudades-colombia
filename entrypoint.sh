#!/bin/bash
set -e

echo "Waiting for database to be ready..."
until python -c "
from database import engine
try:
    engine.connect()
    print('DB ready')
except Exception as e:
    import sys
    print(f'DB not ready: {e}', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; do
  echo "Database not ready, retrying in 2s..."
  sleep 2
done

echo "Running seed..."
python seed.py

echo "Starting application..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
