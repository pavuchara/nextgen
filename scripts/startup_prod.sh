#!/bin/sh
cd django_app
python manage.py migrate
python manage.py collectstatic --no-input
gunicorn blog_nextgen.wsgi:application --bind 0.0.0.0:8000
