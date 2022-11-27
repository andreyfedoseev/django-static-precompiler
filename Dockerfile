FROM andreyfedoseev/django-static-precompiler:18.04-1
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt update && \
    apt install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt install -y  \
    python3.6-dev \
    python3.8-dev \
    python3.9-dev \
    python3.9-distutils \
    python3.10-dev \
    python3.10-distutils \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    sqlite3
RUN mkdir /app
WORKDIR /app
ADD requirements-*.txt /app/
RUN pip3 install -r requirements-test.txt
ADD . /app/
RUN pip3 install -e .[libsass]
