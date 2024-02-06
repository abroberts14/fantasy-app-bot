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

#COPY src/ .
COPY src/ ./src


CMD aerich init-db && aerich upgrade && uvicorn src.main:app --host 0.0.0.0 --port 5000
