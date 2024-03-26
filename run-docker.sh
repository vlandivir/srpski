#!/bin/bash
set -e

# Generate a tag name based on the current date and time (YYYYMMDDHHMM)
TAG_NAME=$(date +%Y%m%d%H%M)

VLANDIVIR_BOT_TOKEN=$(grep TEST_BOT_TOKEN .env | cut -d '=' -f2)
POSTGRES_CONNECTION_STRING=$(grep POSTGRES_CONNECTION_STRING .env | cut -d '=' -f2)
DO_SPACES_ACCESS_KEY=$(grep DO_SPACES_ACCESS_KEY .env | cut -d '=' -f2)
DO_SPACES_SECRET_KEY=$(grep DO_SPACES_SECRET_KEY .env | cut -d '=' -f2)
SENTRY_DSN=$(grep SENTRY_DSN .env | cut -d '=' -f2)


docker build \
  --build-arg VLANDIVIR_BOT_TOKEN="${VLANDIVIR_BOT_TOKEN}" \
  --build-arg TAG_NAME="${TAG_NAME}" \
  --build-arg ENVIRONMENT="DOCKER" \
  --build-arg POSTGRES_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING}" \
  --build-arg DO_SPACES_ACCESS_KEY="${DO_SPACES_ACCESS_KEY}" \
  --build-arg DO_SPACES_SECRET_KEY="${DO_SPACES_SECRET_KEY}" \
  --build-arg SENTRY_DSN="${SENTRY_DSN}" \
  -t vlandivir_bot .

docker stop vlandivir_bot && docker rm vlandivir_bot && docker run --name vlandivir_bot vlandivir_bot
