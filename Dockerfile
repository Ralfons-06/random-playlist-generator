FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

RUN pip install spotipy flask

WORKDIR /app

COPY src ./src
COPY templates ./templates
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY crontab /etc/cron.d/python-cron

RUN chmod 0644 /etc/cron.d/python-cron
RUN crontab /etc/cron.d/python-cron
RUN touch /var/log/cron.log