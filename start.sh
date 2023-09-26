#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
py manage.py migrate

#Starting an app
echo "Starting Django application..."
python manage.py runserver 0.0.0.0:8000