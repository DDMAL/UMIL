FROM python:3.11.5 as build-container
ARG DEVELOPMENT
COPY ./poetry.lock ./pyproject.toml ./web-app/install-packages.sh /virtual-instrument-museum/
WORKDIR /virtual-instrument-museum
RUN chmod u+x /virtual-instrument-museum/install-packages.sh && \
    /virtual-instrument-museum/install-packages.sh $DEVELOPMENT

FROM python:3.11.5 as app-container
ARG DEVELOPMENT
ENV DEVELOPMENT=$DEVELOPMENT
COPY --from=build-container /virtual-instrument-museum/.venv /virtual-instrument-museum/.venv
COPY ./web-app/django-startup.sh /virtual-instrument-museum/
RUN chmod u+x /virtual-instrument-museum/django-startup.sh
RUN apt-get update && \
    apt-get install -y gettext
WORKDIR /virtual-instrument-museum/vim-app
ENV PYTHONPATH="$PYTHONPATH:/virtual-instrument-museum/.venv/lib/python3.11/site-packages/" \
    PATH="$PATH:/virtual-instrument-museum/.venv/bin/"
