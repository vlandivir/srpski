import os
from openai import OpenAI

from dotenv import load_dotenv

load_dotenv('.env')

client = OpenAI(
  api_key = os.getenv('OPEN_API_TEST'),
)

# gpt-3.5-turbo-1106
# gpt-4o

completion = client.chat.completions.create(
  model="gpt-4o",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! Make a new haiku on Russian"}
  ]
)

# Ветры холодны,
# Зимний лес в белых объятьях -
# Тишина снова.

print(completion.choices[0].message)

# models = client.models.list()
# for model in models.data:
#     print(model.id)

# whisper-1
# tts-1
# dall-e-2
# tts-1-hd-1106
# tts-1-hd
# gpt-3.5-turbo-1106
# dall-e-3
# text-embedding-3-small
# text-embedding-3-large
# gpt-3.5-turbo-16k
# babbage-002
# gpt-3.5-turbo-0125
# tts-1-1106
# gpt-3.5-turbo
# gpt-3.5-turbo-instruct
# gpt-3.5-turbo-instruct-0914
# text-embedding-ada-002
# davinci-002