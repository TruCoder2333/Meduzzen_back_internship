#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

#Starting an app
echo "Starting Django application..."
python manage.py runserver 0.0.0.0:8000