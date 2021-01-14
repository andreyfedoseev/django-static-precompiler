FROM andreyfedoseev/django-static-precompiler:18.04
RUN apt-get update && apt-get install -y python3-dev python3-pip sqlite3
RUN mkdir /app
WORKDIR /app
ADD requirements-*.txt /app/
RUN pip3 install -r requirements-dev.txt
ADD . /app/
RUN pip3 install -e .[libsass]
