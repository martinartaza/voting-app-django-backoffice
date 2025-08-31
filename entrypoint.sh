#!/bin/bash

# Exit on any error
set -e

echo "Starting Django application..."

#pip install -r requirements.txt
pip install -r requirements.txt

# Wait for database to be ready
echo "Waiting for database..."
python manage.py wait_for_db

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

# Start the application
echo "Starting Gunicorn..."
#exec gunicorn config.wsgi:application --bind 0.0.0.0:8080
python manage.py runserver 0.0.0.0:8000

