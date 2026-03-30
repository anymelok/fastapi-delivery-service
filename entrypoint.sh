#!/bin/bash
set -e

echo "Running migrations..."
uv run python -m alembic upgrade head

echo "Starting server..."
exec uv run uvicorn src.app:app --host 0.0.0.0 --port 8080
