FROM python:3.5

RUN pip install --upgrade pip
RUN pip install \
    git+https://github.com/Rapptz/discord.py@async \
    tornado \
    parse

WORKDIR /app

CMD ["python3", "main.py"]
