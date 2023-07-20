# Start from an official base image
FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Used to document the host port binding in order to access service running within container locally
EXPOSE 3000

WORKDIR /code/web-app/django

COPY django/requirements.txt /code/web-app/django
COPY django .

RUN pip3 install -r requirements.txt

# Entrypoint command to run when starting container (CMD is used as input argument to ENTRYPOINT)
ENTRYPOINT ["python3", "manage.py", "runserver"]
CMD ["0.0.0.0:3000"]