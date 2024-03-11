# https://habr.com/ru/companies/wunderfund/articles/586778/

FROM python:3.9-slim

COPY keys/srpski-data-e364d16a7d45.json keys/srpski-data-e364d16a7d45.json
COPY keys/ca-certificate.crt keys/ca-certificate.crt

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram-bot .

ARG POSTGRES_CONNECTION_STRING
ENV POSTGRES_CONNECTION_STRING=${POSTGRES_CONNECTION_STRING}

ARG VLANDIVIR_BOT_TOKEN
ENV VLANDIVIR_BOT_TOKEN=${VLANDIVIR_BOT_TOKEN}

ARG TAG_NAME
ENV TAG_NAME=${TAG_NAME}

ARG ENVIRONMENT
ENV ENVIRONMENT=${ENVIRONMENT}

CMD ["python", "vlandivir_bot.py"]
