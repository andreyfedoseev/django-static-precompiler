FROM andreyfedoseev/django-static-precompiler
MAINTAINER Andrey Fedoseev <andrey.fedoseev@gmail.com>
RUN apt-get update && apt-get install -y python2.7-dev python3.5-dev python-pip sqlite3
RUN mkdir /app
WORKDIR /app
ADD requirements-*.txt /app/
RUN pip install -r requirements-dev.txt
ADD . /app/
RUN pip install -e .[libsass]
