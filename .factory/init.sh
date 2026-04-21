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
if ! psql -h localhost -p 5432 -lqt 2>/dev/null | cut -d \| -f 1 | grep -qw copysnipin; then
    echo "Creating database 'copysnipin'..."
    createdb copysnipin 2>/dev/null || echo "Database may already exist"
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
