#!/bin/bash

# Generate a tag name based on the current date and time (YYYYMMDDHHMM)
TAG_NAME=$(date +%Y%m%d%H%M)

export VLANDIVIR_BOT_TOKEN=$(grep TEST_BOT_TOKEN .env | cut -d '=' -f2)

docker build --build-arg VLANDIVIR_BOT_TOKEN="${VLANDIVIR_BOT_TOKEN}" --build-arg TAG_NAME="${TAG_NAME}" -t vlandivir_bot .
docker stop vlandivir_bot && docker rm vlandivir_bot && docker run --name vlandivir_bot vlandivir_bot
