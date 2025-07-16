# Django container
FROM python:3.11.5 as build-container
ARG DEVELOPMENT
COPY ./poetry.lock ./pyproject.toml ./web-app/install-packages.sh /virtual-instrument-museum/
WORKDIR /virtual-instrument-museum
RUN chmod u+x /virtual-instrument-museum/install-packages.sh && \
    /virtual-instrument-museum/install-packages.sh $DEVELOPMENT

# Frontend build stage (only for production)
FROM node:20-slim as frontend-builder
ARG DEVELOPMENT
COPY ./web-app/frontend/ /frontend/
WORKDIR /frontend
# Only install and build for production
RUN if [ "$DEVELOPMENT" != "true" ]; then \
        npm install && \
        npm run sass:build && \
        npm run build; \
    else \
        # Create empty directories for development mode
        mkdir -p /frontend/assets/css /frontend/dist; \
    fi

FROM python:3.11.5 as app-container
ARG DEVELOPMENT
ENV DEVELOPMENT=$DEVELOPMENT
# Copy frontend files
COPY ./web-app/frontend/ /virtual-instrument-museum/frontend/
# Copy built assets for production (empty directories in dev mode)
COPY --from=frontend-builder /frontend/assets/css /virtual-instrument-museum/frontend/assets/css
COPY --from=frontend-builder /frontend/dist /virtual-instrument-museum/frontend/dist

# Install Node.js and frontend dependencies for development only
RUN if [ "$DEVELOPMENT" = "true" ]; then \
        apt-get update && \
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
        apt-get install -y nodejs && \
        rm -rf /var/lib/apt/lists/* && \
        cd /virtual-instrument-museum/frontend && \
        npm install; \
    fi
# Copy Python virtual environment and Django app
COPY --from=build-container /virtual-instrument-museum/.venv /virtual-instrument-museum/.venv
COPY ./web-app/django/ /virtual-instrument-museum/vim-app/
COPY ./web-app/start-up.sh /virtual-instrument-museum/
RUN chmod u+x /virtual-instrument-museum/start-up.sh
WORKDIR /virtual-instrument-museum/
ENV PYTHONPATH="$PYTHONPATH:/virtual-instrument-museum/.venv/lib/python3.11/site-packages/" \
    PATH="$PATH:/virtual-instrument-museum/.venv/bin/"
