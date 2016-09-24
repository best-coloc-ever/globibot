FROM python:3.5

RUN pip install --upgrade pip
RUN pip install \
    discord.py \
    tornado \
    parse \
    git+https://github.com/vlasovskikh/funcparserlib@master \
    twitter \
    youtube-dl \
    psycopg2 \
    pyyaml \
    pillow \
    pynacl \
    git+https://github.com/docker/docker-py@master \
    watchdog \
    cleverbot \
    python-instagram-ext

RUN apt-get update -y && apt-get install -y \
    libopus-dev \
    libav-tools

RUN pip install gtts

ADD . /app
WORKDIR /app

CMD [ \
    "python3", "src/main.py", \
    "--plugin-path", "plugins", \
    "--config-path", "config.yaml" \
]
