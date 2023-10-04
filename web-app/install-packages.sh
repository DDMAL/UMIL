#!/bin/bash

# Install poetry
pip install poetry==1.6.1

poetry config virtualenvs.in-project true
poetry config virtualenvs.options.no-pip true
poetry config virtualenvs.options.no-setuptools true

# Install packages according to the environment
if [[ $1 = "true" ]]
then
    poetry install --no-cache --without dev
else
    poetry install --no-cache --without dev --without debug
fi