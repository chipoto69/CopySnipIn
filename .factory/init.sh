#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel 2>/dev/null || (cd "$SCRIPT_DIR/.." && pwd))"
cd "$PROJECT_DIR"

echo "=== CopySnipIn Environment Setup ==="

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found"
    exit 1
fi
echo "Python: $(python3 --version)"

# Check uv
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv not found. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "uv: $(uv --version)"

# Create database if not exists
if ! command -v psql &>/dev/null || ! command -v createdb &>/dev/null || ! command -v pg_isready &>/dev/null; then
    echo "ERROR: PostgreSQL client tools not found"
    exit 1
fi

if ! pg_isready -h localhost -p 5432 &>/dev/null; then
    echo "ERROR: PostgreSQL not responding on localhost:5432"
    exit 1
fi

if ! psql -h localhost -p 5432 -lqt | cut -d \| -f 1 | grep -qw copysnipin; then
    echo "Creating database 'copysnipin'..."
    createdb -h localhost -p 5432 copysnipin
else
    echo "Database 'copysnipin' exists"
fi

# Check Redis
if redis-cli ping &>/dev/null; then
    echo "Redis: OK"
else
    echo "WARNING: Redis not responding on localhost:6379"
fi

# Install dependencies
if [ -f "uv.lock" ]; then
    echo "Installing dependencies from uv.lock..."
    uv sync --locked
elif [ -f "pyproject.toml" ]; then
    echo "Installing dependencies..."
    uv sync
else
    echo "No pyproject.toml yet - dependencies will be installed when scaffolding is complete"
fi

# Check .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "WARNING: .env file not found. Copy .env.example to .env and fill in API keys."
    fi
else
    echo ".env: OK"
fi

echo "=== Setup Complete ==="
