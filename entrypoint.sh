#!/bin/bash
set -e

# Get PORT from environment or use default
PORT=${PORT:-8000}

# Run migrations
python manage.py migrate --noinput || true

# Start gunicorn
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT}" \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

