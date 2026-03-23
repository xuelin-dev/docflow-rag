#!/usr/bin/env bash
# Run Alembic database migrations.
#
# Usage:
#   ./scripts/migrate.sh              # upgrade to head
#   ./scripts/migrate.sh downgrade -1 # downgrade one revision

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")/backend"

cd "$BACKEND_DIR"

if [ $# -eq 0 ]; then
    echo ">>> Running: alembic upgrade head"
    alembic upgrade head
else
    echo ">>> Running: alembic $*"
    alembic "$@"
fi

echo ">>> Migration complete."
