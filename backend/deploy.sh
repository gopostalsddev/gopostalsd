#!/usr/bin/env bash
set -e

exec gunicorn -b "0.0.0.0:${PORT}" app:app
