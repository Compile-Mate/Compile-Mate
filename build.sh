#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create cache table for database caching
python manage.py createcachetable

# Create superuser if needed (optional)
echo "Build completed successfully!"
