FROM python:3.5

RUN pip install --upgrade pip
RUN pip install \
    discord.py \
    requests

WORKDIR /app

CMD ["python3", "main.py"]
