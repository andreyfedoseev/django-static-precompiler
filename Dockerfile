FROM andreyfedoseev/django-static-precompiler:22.04-1
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt update && \
    apt upgrade --yes && \
    apt autoremove --yes && \
    apt install software-properties-common -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt install -y  \
    python3-venv \
    python3.8-dev \
    python3.8-distutils \
    python3.9-dev \
    python3.9-distutils \
    python3.10-dev \
    python3.10-distutils \
    python3.11-dev \
    python3.11-distutils \
    python3.12-dev \
    python3.13-dev \
    python3-pip \
    sqlite3 && \
    apt clean
ENV POETRY_HOME=/opt/poetry VIRTUAL_ENV=/opt/venv PATH=/opt/venv/bin:/opt/poetry/bin:$PATH
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install --upgrade pip && \
    $POETRY_HOME/bin/pip install poetry && \
    python3 -m venv $VIRTUAL_ENV
WORKDIR /opt/app
ADD . /opt/app/
RUN poetry install --all-extras --no-root --no-interaction && \
    pyright --version && \
    poetry install --all-extras --no-interaction && \
    tox run --notest -- poetry install --all-extras
