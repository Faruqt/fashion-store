#!/bin/bash

# handle database migrations
python manage.py makemigrations

python manage.py migrate

# create superuser if not exists
python scripts/create_admin.py

# start the server
exec gunicorn --bind 0.0.0.0:8000 fashionstore.wsgi:application --timeout 200 --worker-class=gevent --worker-connections=1000 --workers=2 --access-logfile -