#!/usr/bin/env bash
# build.sh — Render build script for PosterMind Django app
# Place this file in your project root (same folder as manage.py)

set -o errexit  # Exit immediately if any command fails

echo "--- Installing dependencies ---"
pip install -r requirements.txt

echo "--- Collecting static files ---"
python manage.py collectstatic --no-input

echo "--- Running database migrations ---"
python manage.py migrate

echo "--- Build complete ---"