#!/usr/bin/env bash
# Start the full local development stack with Docker Compose
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Stadium People Counter development stack..."
cd "$PROJECT_ROOT"
docker compose up --build "$@"
