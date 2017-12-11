#!/bin/sh
# pull images in Dockerfiles referenced by docker-compose.yml
docker pull govready/govready-q-nightly
docker pull centos:7

# pull images directly referenced by docker-compose.yml
docker-compose pull
