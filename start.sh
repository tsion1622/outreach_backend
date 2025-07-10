#!/bin/bash
honcho start
python manage.py migrate

# Start Gunicorn
gunicorn wsgi:application --bind 0.0.0.0:$PORT