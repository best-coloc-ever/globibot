FROM python:3.5

RUN pip install --upgrade pip
RUN pip install \
    git+https://github.com/Rapptz/discord.py@async \
    tornado \
    parse \
    requests \
    twitter \
    youtube-dl \
    pymongo

RUN apt-get update -y && apt-get install -y \
    libopus-dev \
    libav-tools

ADD . /app
WORKDIR /app

CMD ["python3", "src/main.py"]
