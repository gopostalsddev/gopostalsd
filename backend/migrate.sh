#!/usr/bin/env bash
set -euo pipefail

# Run this as a one-shot deployment step before starting/recreating the web
# process. The application factory uses a side-effect-free migration mode.
export FLASK_APP=app.py
export RUN_DB_MIGRATE=1
exec flask db upgrade
