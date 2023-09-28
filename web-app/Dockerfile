FROM python:3.11.5
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN mkdir /virtual-instrument-museum
COPY ./django-startup.sh /virtual-instrument-museum/django-startup.sh
RUN chmod u+x /virtual-instrument-museum/django-startup.sh
WORKDIR /virtual-instrument-museum/vim-app
EXPOSE 8001