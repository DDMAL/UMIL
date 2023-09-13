FROM python:3.11.5
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

WORKDIR /vim-app
CMD ["python", "manage.py", "runserver"]