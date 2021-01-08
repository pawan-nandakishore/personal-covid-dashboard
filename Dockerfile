FROM ubuntu:18.04
LABEL maintainer="Pawan Nandakishore <pawan.nandakishore@gmail.com>"
RUN apt-get update
RUN apt-get install -y python3 python3-dev python3-pip
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN mkdir /app
COPY . /app
COPY ./wsgi.py /app
WORKDIR /app
CMD gunicorn --bind 0.0.0.0:8080 wsgi
