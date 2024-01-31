FROM python:3.11-buster

RUN mkdir app
WORKDIR /app

ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=.

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y postgresql-client

# for migrations
COPY migrations .
COPY pyproject.toml .

COPY src/ .

COPY wait_for_postgres.sh /
RUN chmod +x /wait_for_postgres.sh
