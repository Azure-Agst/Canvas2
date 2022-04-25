#!/bin/bash

# NOTE: this was in prod on the server we used to host the webapp.
#       its important to remember that the repo now lives in my account,
#       rather than the old `fsu-cop4521s` account. therefore this script
#       wont work anymore, but can be used as reference! :)

# pull latest image
echo -e "\npulling latest image..."
docker pull ghcr.io/fsu-cop4521s/canvas2

# if exists, stop the running server
if docker ps | grep canvas2 > /dev/null; then
    echo -e "\nstopping old server..."
    docker stop canvas2
    docker rm canvas2
fi

# start new updated server
echo -e "\nstarting new server..."
docker run -d --name canvas2 --restart unless-stopped --env-file="/home/$(whoami)/.flaskenv.prod" -p 5000:5000 ghcr.io/fsu-cop4521s/canvas2
