# https://habr.com/ru/companies/wunderfund/articles/586778/

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram-bot/vlandivir_bot.py .
COPY telegram-bot/release-cards ./release-cards

ARG VLANDIVIR_BOT_TOKEN
ENV VLANDIVIR_BOT_TOKEN=${VLANDIVIR_BOT_TOKEN}

CMD ["python", "vlandivir_bot.py"]
