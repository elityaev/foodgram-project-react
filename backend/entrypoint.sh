#!/bin/sh
echo "Start makemigrations"
python manage.py makemigrations 2>&1;
echo "Start migrate"
python manage.py migrate 2>&1;
echo "Start loading db"
python manage.py db_load 2>&1;
echo "Start wsgi"
gunicorn yatube.wsgi:application --bind 0.0.0.0:8000 --error-logfile /code/logs/gunicorn.error.log --access-logfile /code/logs/gunicorn.access.log --capture-output --log-level debug
exec "$@"
