#!/bin/sh
docker-compose up -d
docker-compose logs -f | grep 'fully up'
