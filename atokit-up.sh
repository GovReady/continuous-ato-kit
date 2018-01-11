#!/bin/bash

# Ensure images are up to date...

# pull images in Dockerfiles referenced by docker-compose.yml
docker pull govready/govready-q
docker pull centos:7

# pull images directly referenced by docker-compose.yml
docker-compose pull

# Start the containers. Instruct docker-compose to re-build
# images it builds to ensure things are up to date.

if [[ "$0" == "--verbose" ]]; then
  # In verbose mode, run docker-compose in the foreground.
  docker-compose up --build
else
  # In non-verbose mode, detach and then show logs.
  docker-compose up --build -d
  docker-compose logs -f | grep 'fully up'
fi

