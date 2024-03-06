# https://habr.com/ru/companies/wunderfund/articles/586778/

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY telegram-bot/vlandivir_bot.py .
COPY chat-gpt/language-cards/result-images ./result-images

ARG VLANDIVIR_BOT_TOKEN
ENV VLANDIVIR_BOT_TOKEN=${VLANDIVIR_BOT_TOKEN}
ENV CARDS_PATH="result-images"

CMD ["python", "vlandivir_bot.py"]
