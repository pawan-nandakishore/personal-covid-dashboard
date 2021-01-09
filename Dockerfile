FROM ubuntu:18.04
LABEL maintainer="Pawan Nandakishore <pawan.nandakishore@gmail.com>"
RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin
RUN apt-get install -y python3 python3-dev python3-pip 
COPY ./requirements.txt requirements.txt
RUN pip3 install --upgrade pip setuptools
RUN apt-get install git -y 
EXPOSE 8050
RUN pip3 install -r requirements.txt
RUN mkdir /app
COPY . /app
WORKDIR /app
CMD gunicorn --bind 0.0.0.0:8080 --workers=5 wsgi
