FROM python:3.9-slim

WORKDIR /app

COPY telegram-bot/vlandivir_bot.py .
COPY requirements.txt .
COPY chat-gpt/language-cards/result-images ./result-images

RUN pip install --no-cache-dir -r requirements.txt

ARG VLANDIVIR_BOT_TOKEN
ENV VLANDIVIR_BOT_TOKEN=${VLANDIVIR_BOT_TOKEN}
ENV CARDS_PATH="result-images"

CMD ["python", "vlandivir_bot.py"]
