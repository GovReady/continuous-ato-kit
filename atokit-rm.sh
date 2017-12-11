#!/bin/sh
docker-compose rm -s
docker-compose down -v --rmi all
echo "\nNOTE: 'not found' errors are okay and to be expected if this script is run after atokit-down.sh, or if this script is run more than once.\n"
