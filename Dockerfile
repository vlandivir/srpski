# https://habr.com/ru/companies/wunderfund/articles/586778/

FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libffi-dev g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY keys/srpski-data-e364d16a7d45.json keys/srpski-data-e364d16a7d45.json
COPY keys/ca-certificate.crt keys/ca-certificate.crt

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-dev

COPY telegram-bot .

ARG POSTGRES_CONNECTION_STRING
ENV POSTGRES_CONNECTION_STRING=${POSTGRES_CONNECTION_STRING}

ARG VLANDIVIR_BOT_TOKEN
ENV VLANDIVIR_BOT_TOKEN=${VLANDIVIR_BOT_TOKEN}

ARG TAG_NAME
ENV TAG_NAME=${TAG_NAME}

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}

ARG DO_SPACES_ACCESS_KEY
ENV DO_SPACES_ACCESS_KEY=${DO_SPACES_ACCESS_KEY}

ARG DO_SPACES_SECRET_KEY
ENV DO_SPACES_SECRET_KEY=${DO_SPACES_SECRET_KEY}

ARG SENTRY_DSN
ENV SENTRY_DSN=${SENTRY_DSN}

CMD ["python", "vlandivir_bot.py"]
