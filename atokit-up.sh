#!/bin/sh
docker-compose up -d
docker-compose logs -f | egrep 'fully up|Applying socialaccount'
