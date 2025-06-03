# Frontend dependency install
FROM node:20 as frontend-install
COPY ./web-app/frontend/ /virtual-instrument-museum/frontend/
WORKDIR /virtual-instrument-museum/frontend
RUN npm install

# Django container
FROM python:3.11.5 as build-container
ARG DEVELOPMENT
COPY ./poetry.lock ./pyproject.toml ./web-app/install-packages.sh /virtual-instrument-museum/
WORKDIR /virtual-instrument-museum
RUN chmod u+x /virtual-instrument-museum/install-packages.sh && \
    /virtual-instrument-museum/install-packages.sh $DEVELOPMENT

FROM python:3.11.5 as app-container
ARG DEVELOPMENT
ENV DEVELOPMENT=$DEVELOPMENT
# install node 20
RUN apt-get update && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs
# copy frontend
COPY --from=frontend-install /virtual-instrument-museum/frontend/node_modules /virtual-instrument-museum/frontend/node_modules
# copy django
COPY --from=build-container /virtual-instrument-museum/.venv /virtual-instrument-museum/.venv
COPY ./web-app/start-up.sh /virtual-instrument-museum/
RUN chmod u+x /virtual-instrument-museum/start-up.sh
WORKDIR /virtual-instrument-museum/
ENV PYTHONPATH="$PYTHONPATH:/virtual-instrument-museum/.venv/lib/python3.11/site-packages/" \
    PATH="$PATH:/virtual-instrument-museum/.venv/bin/"
