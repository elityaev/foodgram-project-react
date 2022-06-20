#!/bin/sh
echo "Start makemigrations"
python manage.py makemigrations /dev/null 2>&1;
echo "Start migrate"
python manage.py migrate /dev/null 2>&1;
echo "Start loading db"
python manage.py db_load /dev/null 2>&1;
echo "Start wsgi"
gunicorn yatube.wsgi:application --bind 0.0.0.0:8000 --error-logfile /code/logs/gunicorn.error.log --access-logfile /code/logs/gunicorn.access.log --capture-output --log-level debug
exec "$@"
