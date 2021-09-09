FROM python:3.8
RUN mkdir /app
WORKDIR /app
RUN apt update
RUN apt install -y mariadb-client
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/