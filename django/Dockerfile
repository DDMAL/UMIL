FROM python:3.10

WORKDIR /django

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .