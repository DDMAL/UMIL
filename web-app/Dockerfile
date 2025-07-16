# Common build container
FROM python:3.11.5 AS builder
ARG TARGET

WORKDIR /virtual-instrument-museum
COPY ./poetry.lock ./pyproject.toml /virtual-instrument-museum/

RUN pip install poetry==1.8.3

RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.options.no-pip true
RUN poetry config virtualenvs.options.no-setuptools true


# -------- DEVELOPMENT IMAGE --------
FROM builder AS dev
RUN mkdir -p /frontend/assets/css /frontend/dist

# Copy frontend files
COPY ./web-app/frontend/ /virtual-instrument-museum/frontend/

# Install Node.js and frontend dependencies for development only
RUN apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \

WORKDIR /frontend
RUN npm install

# Copy Python virtual environment and Django app
COPY --from=build-container /virtual-instrument-museum/.venv /virtual-instrument-museum/.venv
COPY ./web-app/django/ /virtual-instrument-museum/vim-app/
WORKDIR /virtual-instrument-museum/
RUN poetry install --no-cache --without dev

ENV PYTHONPATH="$PYTHONPATH:/virtual-instrument-museum/.venv/lib/python3.11/site-packages/" \
    PATH="$PATH:/virtual-instrument-museum/.venv/bin/"

# Development mode: run frontend dev server in background
RUN \
    cd /virtual-instrument-museum/frontend \
    npm run sass:watch & \
    npm run dev -- --host 0.0.0.0 & \
    # run django dev server
    cd /virtual-instrument-museum/vim-app \
    python manage.py collectstatic --noinput \
    python manage.py runserver_plus 0:8001

# -------- PRODUCTION IMAGE --------
FROM node:20-slim AS prod-frontend
COPY ./web-app/frontend/ /frontend/
WORKDIR /frontend
RUN npm install && \
        npm run sass:build && \
        npm run build \
# Copy built assets for production (empty directories in dev mode)
COPY --from=prod-frontend /frontend/assets/css /virtual-instrument-museum/frontend/assets/css
COPY --from=prod-frontend /frontend/dist /virtual-instrument-museum/frontend/dist


FROM builder AS prod


FROM python:3.11.5 as app-container

RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.options.no-pip true
RUN poetry config virtualenvs.options.no-setuptools true
# Install poetry dependencies for production: without debug
RUN poetry install --no-cache --without dev --without debug

# Production mode: assets already built during Docker build
# Just run django server with gunicorn
RUN \
    cd /virtual-instrument-museum/vim-app \
    python manage.py collectstatic --noinput \
    gunicorn -w 2 -b 0:8001 VIM.wsgi