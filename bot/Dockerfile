FROM python:3.5

RUN pip install --upgrade pip
RUN pip install \
    discord.py \
    tornado \
    parse \
    funcparserlib \
    twitter \
    youtube-dl \
    psycopg2 \
    pyyaml \
    pillow \
    pynacl \
    git+https://github.com/docker/docker-py@master \
    watchdog

RUN apt-get update -y && apt-get install -y \
    libopus-dev \
    libav-tools

ADD . /app
WORKDIR /app

CMD ["python3", "src/main.py"]
