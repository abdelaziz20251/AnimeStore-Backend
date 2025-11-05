# Production Dockerfile for Railway/Docker deployment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories for database and media
RUN mkdir -p /app/db /app/media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port (Railway will set PORT env var at runtime)
# Use default port 8000 for EXPOSE, Railway will override at runtime
EXPOSE 8000

# Start command - use PORT environment variable
CMD sh -c "gunicorn config.wsgi:application --bind 0.0.0.0:\${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -"
