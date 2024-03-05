## Srpski

### Docker
VLANDIVIR_BOT_TOKEN=$(grep VLANDIVIR_BOT_TOKEN .env | cut -d '=' -f2) \
docker build --build-arg VLANDIVIR_BOT_TOKEN="${VLANDIVIR_BOT_TOKEN}" -t vlandivir_bot .

docker stop vlandivir_bot && docker rm vlandivir_bot && docker run --name vlandivir_bot vlandivir_bot
