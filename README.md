# Continuous ATO Kit

This repository contains an example for integrating federal cybersecurity compliance practices into an agile continuous integration/continuous deployment pipeline.

In this example, we use Jenkins (a build pipeline), GovReady-Q (a compliance server), and Docker (virtualization), but the architecture could be adapted to other setups.

## Architecture

### Systems

This pipeline example assumes seven system components:

* The **Application Source Code Repository**, such as a Github repository, containing the application being built. In this example we will build GovReady-Q.
* A **Docker Host Machine** running the Docker daemon, which could be your workstation.
* A **Build Server**, in this case Jenkins running in a Docker container on the host machine.
* A **Security and Monitoring Server** (TODO).
* A **Compliance Server**, in this case GovReady-Q running in a Docker container on the host machine.
* The **Target Application Server** to which the application is being deployed, in this case an ephemeral Docker container created during the build.
* The **DevSecOps Engineer's (Your) Workstation**, which has a web browser that the engineer will use to access the Compliance Server to inspect compliance artifacts generated during the build. This workstation might be the same as the Docker Host Machine.

## Steps to Create the Pipeline

### Step 1: Get This Kit

Get the Continuous ATO Kit by cloning this repository onto the **Docker Host Machine**.

	git clone https://github.com/GovReady/continuous-ato-kit

### Step 2: Set Up The Pipeline Environment

#### Install Docker

First [install Docker](https://docs.docker.com/engine/installation/) on the **Docker Host Machine** and, if appropriate, [grant non-root users access to run Docker containers](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user) (or else use `sudo` when invoking Docker below).

#### Start the Jenkins Build Server

On the **Docker Host Machine**, start the Jenkins build server:

	docker run \
		--name jenkins --rm \
		-u root \
		-p 8080:8080 \
		-v jenkins-data:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock
		 jenkinsci/blueocean

(We plan to build the application from its source code repository on Github. If you need to clone the application onto the Docker Host Machine, bind mount the clone directory into the Jenkins container by adding `-v /path/to/application/code:/home` to the arguments above before the last argument.)

#### Start the Security/Testing Server

TODO

#### Start the GovReady-Q Compliance Server

##### Start the Docker container

Start the **Compliance Server**, which will be a Docker container running GovReady-Q. GovReady-Q provides a shell script to make it easy to start it in a Docker container. Get the shell script from the GovReady-Q Github repository and save it on the **Docker Host Machine**:

	curl -s -o docker_container_run.sh https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh

The run it to start the compliance server in the background listening on port 8000 on the **Docker Host Machine** and on a hostname `govready-q` that we'll create an alias for in a moment:

	./docker_container_run.sh --relaunch --address govready-q:8000

##### Set up Docker networking

While the container is starting, set up the Docker network so that the **Target Application Server** can communicate with the **Compliance Server**. We will use a Docker User Defined Network, which is a private virtual network, to connect the containers. Create a network named `continuousato` and then add the Compliance Server container to it:

	docker network create continuousato
	docker network connect continuousato govready-q

The Compliance Server will be known as `govready-q` on the Docker network.

The **Target Application Server** will be added to the network through the application's Jenkinsfile.

Although the two containers communicate through the Docker User Defined Network, the **DevSecOps Engineer's Workstation** will connect to the **Compliance Server** via regular networking through Docker port forwarding. The Compliance Server is already listening on port `8000` on the **Docker Host Machine**. Add an alias in the `/etc/hosts` file on the **DevSecOps Engineer's Workstation** for `govready-q` so that the Compliance Server can be reached at the same address as on the Docker network. If the **DevSecOps Engineer's Workstation** is the same machine as the **Docker Host Machine**, use the loopback address:

	127.0.0.1	govready-q

If the machines are different, use the IP address of the **Docker Host Machine**.

##### Start the Compliance App

Open the GovReady-Q Compliance Server in a web browser on the **DevSecOps Engineer's Workstation** at `http://govready-q:8000`. It may take a few more moments for the server to become ready. Once a login screen appears, return to the **Host Machine** command line to create GovReady-Q's first user account:

	docker container exec -it govready-q ./first_run.sh

Follow the prompts:

	TODO: Show output.

TODO....

* Log into the Django admin and add an AppSource for the GovReady-Q sample apps at https://github.com/GovReady/govready-sample-apps.

* Use GovReady-Q to start a new compliance app.

* Get its API URL.

* Get your write-only API key from the API Keys page.

All of the steps in this section (Start the GovReady-Q Compliance Server) are automated by a script named `provision_compliance_server.sh`.

#### Review the Environment

TODO. docker command or portainer.io screenshot; login and dashboards of Jenkins and GovReady.


### Step 3: Set Up Your Target App to Build

#### Configure Jenkins to Build the Application

* TODO. Add configuration.

* TODO. Review target app's Jenkinsfile.

#### Provide Compliance Server Credentials

In Jenkins, go to the Credentials page.

![](jenkins-credentials-1.png)

Add two `Secret Text` credentials. The first looks like:

![](jenkins-credentials-2.png)

Set the `govready_q_api_url` and `govready_q_api_key` credentials to the URL and API key retreived when setting up the Compliance Server.

### Step 4: Build the Application and View Compliance Artifacts

* Start the build.
* View the results in the GovReady-Q Compliance Server.

### Step 5: Tear-down

Stop the **Build Server** (Jenkins) container simply by typing CTRL+C into its terminal. The container will be automatically removed.

Remove the **Compliance Server** container using:

	docker container rm -f govready-q

