#!/bin/bash

if [[ $DEVELOPMENT = "true" ]]
then
    # Development mode: run frontend dev server in background
    cd /virtual-instrument-museum/frontend
    npm run sass:watch &
    npm run dev -- --host 0.0.0.0 &
    # run django dev server
    cd /virtual-instrument-museum/vim-app
    python manage.py collectstatic --noinput
    python manage.py runserver_plus 0:8001
else
    # Production mode: assets already built during Docker build
    # Just run django server with gunicorn
    cd /virtual-instrument-museum/vim-app
    python manage.py collectstatic --noinput
    gunicorn -w 2 -b 0:8001 VIM.wsgi
fi
