#!/bin/bash

if [[ $DEVELOPMENT = "true" ]]
then
    python manage.py runserver 0:8001
else
    gunicorn -w 2 -b 0:8001 VIM.wsgi
fi