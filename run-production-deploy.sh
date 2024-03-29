#!/bin/bash
set -e

# Generate a tag name based on the current date and time (YYYYMMDDHHMM)
TAG_NAME=$(date +%Y%m%d%H%M)

# Load the server IP address from server_ip.txt
SERVER_IP=$(grep DIGITAL_OCEAN_IP .env | cut -d '=' -f2)

# Extract VLANDIVIR_BOT_TOKEN from .env
VLANDIVIR_BOT_TOKEN=$(grep VLANDIVIR_BOT_TOKEN .env | cut -d '=' -f2)
POSTGRES_CONNECTION_STRING=$(grep POSTGRES_CONNECTION_STRING .env | cut -d '=' -f2)
DO_SPACES_ACCESS_KEY=$(grep DO_SPACES_ACCESS_KEY .env | cut -d '=' -f2)
DO_SPACES_SECRET_KEY=$(grep DO_SPACES_SECRET_KEY .env | cut -d '=' -f2)
SENTRY_DSN=$(grep SENTRY_DSN .env | cut -d '=' -f2)

docker build \
  --build-arg VLANDIVIR_BOT_TOKEN="${VLANDIVIR_BOT_TOKEN}" \
  --build-arg TAG_NAME="${TAG_NAME}" \
  --build-arg ENVIRONMENT="PROD" \
  --build-arg POSTGRES_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING}" \
  --build-arg DO_SPACES_ACCESS_KEY="${DO_SPACES_ACCESS_KEY}" \
  --build-arg DO_SPACES_SECRET_KEY="${DO_SPACES_SECRET_KEY}" \
  --build-arg SENTRY_DSN="${SENTRY_DSN}" \
  -t vlandivir_bot .

docker tag vlandivir_bot registry.digitalocean.com/vlandivir-main/vlandivir_bot:$TAG_NAME
docker push registry.digitalocean.com/vlandivir-main/vlandivir_bot:$TAG_NAME

# Update the Docker container on the DigitalOcean droplet
SSH_COMMANDS="docker pull registry.digitalocean.com/vlandivir-main/vlandivir_bot:$TAG_NAME; \
docker stop vlandivir_bot; \
docker rm vlandivir_bot; \
docker run -d -p 80:80 --name vlandivir_bot registry.digitalocean.com/vlandivir-main/vlandivir_bot:$TAG_NAME"

ssh -o StrictHostKeyChecking=no root@$SERVER_IP "$SSH_COMMANDS"
