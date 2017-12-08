#!/bin/sh
docker-compose rm -s
docker-compose down -v --rmi local
