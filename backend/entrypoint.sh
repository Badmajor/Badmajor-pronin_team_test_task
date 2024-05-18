#!/bin/sh

python manage.py migrate

python manage.py collectstatic

cp -r /backend/static/. /static/

gunicorn --bind 0.0.0.0:8000 config.wsgi