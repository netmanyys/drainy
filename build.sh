#!/bin/bash

sudo echo 'y' | sudo docker system prune -a
version_id=0.93
sudo docker build -t yunshengyan/drainy:$version_id .
sudo docker push yunshengyan/drainy:$version_id

echo "Build completed!"