#!/bin/bash

python manage.py collectstatic --noinput

if [[ $DEVELOPMENT = "true" ]]
then
    python manage.py runserver_plus 0:8001
else
    gunicorn -w 2 -b 0:8001 VIM.wsgi
fi