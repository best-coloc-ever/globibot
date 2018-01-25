FROM python:3.5

RUN apt-get update -y && apt-get install -y \
    libopus-dev \
    libav-tools \
    tesseract-ocr

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
    docker-py \
    watchdog \
    cleverbot \
    python-instagram-ext \
    gtts \
    humanize

RUN curl -L https://nodejs.org/dist/v8.9.4/node-v8.9.4-linux-x64.tar.xz \
        | tar xJ --strip-components=1 -C /usr/ &&\
    ACCEPT_HIGHCHARTS_LICENSE=YES npm i -g highcharts-export-server --unsafe-perm

ADD . /app
WORKDIR /app

CMD [ \
    "python3", "src/main.py", \
    "--plugin-path", "plugins", \
    "--config-path", "config.yaml" \
]
