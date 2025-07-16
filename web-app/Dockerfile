# -------- Build stage --------
FROM python:3.11.5 AS builder
ARG MODE

WORKDIR /virtual-instrument-museum/
COPY ./poetry.lock ./pyproject.toml /virtual-instrument-museum/

RUN pip install poetry==1.8.3

RUN poetry config virtualenvs.in-project true
RUN poetry config virtualenvs.options.no-pip true
RUN poetry config virtualenvs.options.no-setuptools true
RUN poetry install --without dev

# -------- DEVELOPMENT IMAGE --------
FROM builder AS dev
COPY --from=builder /virtual-instrument-museum/.venv /virtual-instrument-museum/.venv
COPY ./web-app/django/ /virtual-instrument-museum/vim-app/
COPY ./web-app/frontend/ /virtual-instrument-museum/frontend/

RUN mkdir -p /frontend/assets/css /frontend/dist

# Install Node.js and frontend dependencies
RUN apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/* && \
    cd /virtual-instrument-museum/frontend && \
    npm install

WORKDIR /virtual-instrument-museum/

ENV PYTHONPATH="$PYTHONPATH:/virtual-instrument-museum/.venv/lib/python3.11/site-packages/" \
    PATH="$PATH:/virtual-instrument-museum/.venv/bin/"

# Development mode: run frontend dev server in background
CMD bash -c "\
    cd frontend \
    npm run sass:watch & \
    npm run dev -- --host 0.0.0.0 & \
    cd /virtual-instrument-museum/vim-app \
    python manage.py collectstatic --noinput \
    python manage.py runserver_plus 0:8001"


# ==================================
# -------- PRODUCTION IMAGE --------
FROM node:20-slim AS prod-frontend
COPY ./web-app/frontend/ /frontend/
WORKDIR /frontend
RUN npm install && \
        npm run sass:build && \
        npm run build

FROM builder AS prod
COPY --from=builder /virtual-instrument-museum/.venv /virtual-instrument-museum/.venv
COPY ./web-app/django/ /virtual-instrument-museum/vim-app/
COPY ./web-app/frontend/ /virtual-instrument-museum/frontend/

COPY --from=prod-frontend /frontend/assets/css /virtual-instrument-museum/frontend/assets/css
COPY --from=prod-frontend /frontend/dist /virtual-instrument-museum/frontend/dist

# Install poetry dependencies for production: without debug
RUN poetry install --no-cache --without dev --without debug

ENV PYTHONPATH="$PYTHONPATH:/virtual-instrument-museum/.venv/lib/python3.11/site-packages/" \
    PATH="$PATH:/virtual-instrument-museum/.venv/bin/"

# Production mode: assets already built during Docker build
# Just run django server with gunicorn
CMD bash -c "cd /virtual-instrument-museum/vim-app \
    python manage.py collectstatic --noinput \
    gunicorn -w 2 -b 0:8001 VIM.wsgi"