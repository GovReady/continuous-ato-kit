#!/bin/bash
#############################################################################################
# This script provisions a GovReady-Q Compliance Server into which
# application server security scan test results will be stored.
#
# The script requires that docker, 'curl' and 'jq' be installed.
#
# This script begins by performing administrative functions that
# would normally be done manually by the compliance server system
# administrator:
#
# * Start a new Docker container named govready-q that runs GovReady-Q.
#
# * Configure GovReady-Q by setting up its organization and first
#   user named "demo".
#
# * For the purposes of the demo, peer into the GovReady-Q database
#   to get the user's read-write API Key that will be given to the
#   Continuous Integration Pipeline for pushing scan test results.
#   Normally a user would visit GovReady-Q in their browser, log in,
#   and then download their API key.
#
# * Configure GovReady-Q to have an AppSource called "samples" that
#   points to the GovReady Sample Apps at https://github.com/GovReady/govready-sample-apps.
#
# * Start the Generic Unix File Server sample app ("unix_file_server")
#   from the sample apps repository.
#
# * For the purpopses of the demo, import unix_file_server.json, which
#   are some question answers that we've already exported and saved in
#   this repository, so that they do not have to be entered by hand.
#
# * Output the API URL to the GovReady-Q Compliance Server that the Continuous
#   Integration Pipeline will need to save security scan results.
#############################################################################################

set -euf -o pipefail # abort script on error

# Start a new Docker container that runs GovReady-Q
###################################################

# Get our helper script from Github.
echo "Downloading docker_container_run.sh..."
curl -s -o docker_container_run.sh https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
chmod +x docker_container_run.sh

# Provision a Docker User Defined Network if one has not already been created.
if ! docker network ls | grep "\scontinuousato\s" > /dev/null; then
	docker network create continuousato
fi

if ! grep "^127.0.0.1\s\s*govready-q$" /etc/hosts > /dev/null; then
	echo "Hang on, it looks like you didn't add govready-q to your /etc/hosts"
	echo "file on the host machine. You should add:"
	echo
	echo "127.0.0.1	govready-q"
	exit 1
fi

# Start container. 
#
# The container will get its default name 'govready-q'
# and we'll tell Q that its hostname will be the same, since we'll
# allow docker user-defined networks to make the container discoverable
# by its name. We'll connect it to a pre-made network in a second step.
#
# The caller of this script can set additional arguments by putting
# them in an environment variable named DOCKER_ARGS, like to change
# the image being started.
echo "Starting GovReady-Q docker container..."
./docker_container_run.sh --relaunch --address govready-q:8000 ${DOCKER_ARGS-}
docker network connect continuousato govready-q
echo

# Wait for container to be ready, i.e. the database is initialized,
# which is indicated by the presence of a file named "ready".
while ! docker container exec govready-q test -f ready; do
	# Database is not initialized yet.
	echo "Waiting for the GovReady-Q database to finish initializing..."
	sleep 4
done

echo

# Run the following in Python in the container's environment.
# The Python code sets up the container and outputs information
# for calling the API, which we redirect to save in q.json on
# the host.
docker container exec -i govready-q python <<EOF > q.json;
# initialize django
import os; os.environ.setdefault("DJANGO_SETTINGS_MODULE", "siteapp.settings")
import django; django.setup()

import json

from siteapp.models import User, Organization, Folder
from guidedmodules.models import AppSource
from siteapp.views import start_app

# Set up a User named "demo" and print its API key.
###################################################
user, is_new = User.objects.get_or_create(username='demo')
password = "1234"
user.set_password(password)

# Set up a new Organization and make the user an admin of it.
#############################################################
org = Organization.objects.filter(subdomain="main").first()
if not org:
  org = Organization.create(name='Department of Demonstrations', subdomain="main", admin_user=user)

# Add an AppSource called "samples".
####################################
appsrc, is_new = AppSource.objects.get_or_create(namespace="demo")
appsrc.spec = { 'type': "git", "url": "https://github.com/GovReady/tacr-demo-apps" }
appsrc.save()

# Start the app.
################
folder = Folder.objects.create(organization=org, title="App Folder")
project = start_app("demo/unix_file_server", org, user, folder, None, None)

# Import some saved data for this app.
# TODO

# Output the API call info.
###########################
# Communicate to the host machine the credentials of the demo user
# using JSON, so that we can continue scripting it below.
print(json.dumps({
	"username": user.username,
	"password": password,
	"url": project.get_api_url(),
	"key": user.get_api_keys()['rw'],
}, indent=2))
EOF

# Back on the host machine...

echo "demo username = $(jq -r .username q.json)"
echo "demo user password = $(jq -r .password q.json)"
echo "govready_q_api_url = $(jq -r .url q.json)"
echo "govready_q_api_key = $(jq -r .key q.json)"

exit 0

# Test that everything is working. Submit an HTTP POST to the app.
EXPECTED=hello.govready.com
curl -s \
	-F project.file_server.hostname=$EXPECTED \
	--header "Authorization: $(jq -r .key q.json)" \
	$(jq -r .url q.json)

# Check that it has the right value.
ACTUAL=$(curl -s \
	--header "Authorization: $(jq -r .key q.json)" \
	$(jq -r .url q.json) \
	| jq -r .project.file_server.hostname)
if [[ "$ACTUAL" != "$EXPECTED" ]]; then
	echo "Test API call failed (got $ACTUAL, should be $EXPECTED)."
	exit 1
fi

# Initialize the app with an HTTP POST with JSON and check the result.
curl -s \
	--header "Authorization: $(jq -r .key q.json)" \
	-XPOST --data @file_server_initial_data.json \
    --header "Content-Type: application/json" \
	$(jq -r .url q.json)
