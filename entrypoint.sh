#!/bin/bash

# Exit on any error
set -e

echo "Starting Django application..."

# Install dependencies
pip install -r requirements.txt

# Wait for database to be ready
echo "Waiting for database..."
python manage.py wait_for_db

# RESET DATABASE OPTION (for first deploy only - remove after first successful deploy)
# Set RESET_DATABASE=true in Cloud Run environment variables for first deploy
if [ "$RESET_DATABASE" = "true" ]; then
    echo "⚠️  RESET_DATABASE is enabled - Dropping all tables..."
    python manage.py migrate --run-syncdb
    python manage.py migrate --fake-initial
    echo "Database reset completed. Remember to remove RESET_DATABASE env var after first deploy!"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py create_superuser_if_not_exists

# Set up production site
echo "Setting up production site..."
python manage.py setup_production_site

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application with Gunicorn on port 8080 (required by Cloud Run)
echo "Starting Gunicorn on port 8080..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - --log-level info

