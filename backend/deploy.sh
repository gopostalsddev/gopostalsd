#!/usr/bin/env bash
set -e

export FLASK_APP=app.py
export RUN_DB_MIGRATE=1
flask db upgrade
unset RUN_DB_MIGRATE
exec gunicorn -b "0.0.0.0:${PORT}" app:app
