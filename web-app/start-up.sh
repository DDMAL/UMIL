#!/bin/bash

if [[ $DEVELOPMENT = "true" ]]
then
    # run frontend dev server in background
    cd /virtual-instrument-museum/frontend
    npm run dev -- --host 0.0.0.0 &
    # run django dev server
    cd /virtual-instrument-museum/vim-app
    python manage.py collectstatic --noinput
    python manage.py runserver_plus 0:8001
else
    # run frontend build
    cd /virtual-instrument-museum/frontend
    npm run build
    # run django server
    cd /virtual-instrument-museum/vim-app
    python manage.py collectstatic --noinput
    gunicorn -w 2 -b 0:8001 VIM.wsgi
fi
