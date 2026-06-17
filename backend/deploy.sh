#!/usr/bin/env bash
set -e

export FLASK_APP=app.py

flask db upgrade
exec gunicorn -b "0.0.0.0:${PORT}" app:app
