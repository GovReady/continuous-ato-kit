#!/bin/sh
docker-compose rm -s
docker-compose down -v --rmi local
echo "\nNOTE: 'not found' errors are okay and to be expected if this script is run before atokit-up.sh, or if this script is run more than once.\n"
