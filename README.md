## Srpski

### Update inages
```
python3 chat-gpt/language-cards/add-text-to-images.py
python3 chat-gpt/google_db/google_db_save_cards.py
```

### Local Docker Test
```
./run-docker.sh
```

### Release
```
./run-production-deploy.sh
```

### Digital Ocean
```
brew install doctl

# create API token in DO
doctl auth init

# create registry in DO
doctl registry login

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
