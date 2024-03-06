## Srpski

### Docker
```
VLANDIVIR_BOT_TOKEN=$(grep VLANDIVIR_BOT_TOKEN .env | cut -d '=' -f2) \
docker build --build-arg VLANDIVIR_BOT_TOKEN="${VLANDIVIR_BOT_TOKEN}" -t vlandivir_bot .

docker stop vlandivir_bot && docker rm vlandivir_bot && docker run --name vlandivir_bot vlandivir_bot
```

### Digital Ocean
```
brew install doctl

# create API token in DO
doctl auth init

# create registry in DO
doctl registry login

registry.digitalocean.com/

docker tag vlandivir_bot registry.digitalocean.com/vlandivir-main/vlandivir_bot:202403062207
docker push registry.digitalocean.com/vlandivir-main/vlandivir_bot:202403062207
# 202403062207: digest: sha256:8286e3a305d516ce32d5ffd24e42317907184fda09d3b477a727c6288ed79cf0 size: 2413

# run on droplet
ssh root@aa.bb.cc.dd
sudo snap install doctl
mkdir ~/.config
sudo snap connect doctl:dot-docker
doctl auth init
doctl registry login --never-expire

docker pull registry.digitalocean.com/vlandivir-main/vlandivir_bot:202403062207
docker run -d -p 80:80 registry.digitalocean.com/vlandivir-main/vlandivir_bot:202403062207
```
