# Continuous ATO Kit

This repository contains an example for integrating federal cybersecurity compliance practices into an agile continuous integration/continuous deployment (CI/CD) pipeline.

In this example, we use Jenkins (a build pipeline), GovReady-Q (a compliance server), OpenSCAP (a security and testing server), a Target Application (a target app to build), and Docker (virtualization). This architecture could be adapted to other other choices of tool and other setups.

## Architecture

### Pipeline Servers

This pipeline example models seven common pipeline components:

* The **Application Source Code Repository**, such as a Github repository, containing the application being built. In this example we will build GovReady-Q.
* A **Docker Host Machine** running the Docker daemon, which could be your workstation.
* A **Build Server**, in this case Jenkins running in a Docker container on the host machine.
* A **Security and Monitoring Server** (TODO).
* A **Compliance Server**, in this case GovReady-Q running in a Docker container on the host machine. The Compliance Server provides an API for storing testing evidence and generates a system security plan.
* The **Target Application Server** to which the application is being deployed, in this case an ephemeral Docker container created during the build.
* The **DevSecOps Engineer’s (Your) Workstation**, which has a web browser that the engineer will use to access the Compliance Server to inspect compliance artifacts generated during the build. This workstation might be the same as the Docker Host Machine.

![](docs/c-a-k-20171117-002.png)

## Steps to Create the Pipeline

### Step 1: Get This Kit

Get the Continuous ATO Kit by cloning this repository onto the **Docker Host Machine**.

	git clone https://github.com/GovReady/continuous-ato-kit

### Step 2: Set Up The Pipeline Environment

#### Install Docker

First [install Docker](https://docs.docker.com/engine/installation/) on the **Docker Host Machine** (if on a Linux machine, you may want to [grant non-root users access to run Docker containers](https://docs.docker.com/engine/installation/linux/linux-postinstall/#manage-docker-as-a-non-root-user)).

#### Start the Jenkins Build Server

On the **Docker Host Machine**, start the Jenkins build server:

	docker run \
		--name jenkins --rm \
		-u root \
		-p 8080:8080 \
		-v jenkins-data:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock \
		 jenkinsci/blueocean

See the [Jenkins documentation](https://jenkins.io/doc/tutorials/building-a-node-js-and-react-app-with-npm/) for further information about starting Jenkins.

*Advanced*. We will build the application from its source code repository on Github, but you can also build from a local git repository using a Docker bind mount (`-v`) and using a different Jenkins configuration below.

Check that Jenkins is now running at `http://localhost:8080/` on the **Docker Host Machine**.

We’re running Jenkins in the foreground so you can watch the terminal output. Leave that running and open a new terminal for the steps below.

#### Start the Security/Testing Server

(TODO - not yet implemented)

#### Start the GovReady-Q Compliance Server

The **Compliance Server** is a Docker container running GovReady-Q. In this section we start the container, set up GovReady-Q, and begin a Compliance App. The Compliance App provides an API for storing testing evidence and generates a system security plan.

##### Launch GovReady-Q

GovReady-Q provides a shell script to make it easy to start it in a Docker container. Get the shell script from the GovReady-Q Github repository and save it on the **Docker Host Machine**:

	curl -s -o docker_container_run.sh https://raw.githubusercontent.com/GovReady/govready-q/master/deployment/docker/docker_container_run.sh
	chmod +x docker_container_run.sh

Run it to start the compliance server in the background:

	./docker_container_run.sh --relaunch --address govready-q:8000

##### Set up networking

While the container is starting, set up the Docker network so that the **Target Application Server** can communicate with the **Compliance Server**. We will use a Docker User Defined Network, which is a private virtual network, to connect the containers. Create a network named `continuousato` and then add the Compliance Server container to it:

	docker network create continuousato
	docker network connect continuousato govready-q

The Compliance Server will be known as `govready-q` on the Docker network.

The **Target Application Server** will be added to the network through the application’s Jenkinsfile.

Although the two containers communicate through the Docker User Defined Network, the **DevSecOps Engineer’s Workstation** will connect to the **Compliance Server** via regular networking and Docker port forwarding. The Compliance Server is already listening on port `8000` on the **Docker Host Machine**. Add an alias in the `/etc/hosts` file on the **DevSecOps Engineer’s Workstation** for `govready-q` so that the Compliance Server can be reached easily. If the **DevSecOps Engineer’s Workstation** is the same machine as the **Docker Host Machine**, use the loopback address:

	127.0.0.1	govready-q

If the machines are different, use the IP address of the **Docker Host Machine**.

##### Start the Compliance App

Open the GovReady-Q Compliance Server in a web browser on the **DevSecOps Engineer’s Workstation** at `http://govready-q:8000`. It may take a few more moments for the server to become ready. Once a login screen appears, return to the **Host Machine** command line to create GovReady-Q’s first user account:

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


### Step 3: Set Up the Target App to Build, Test and ATO with the Pipeline

#### Configure Jenkins to Build the Application

For the purposes of this demo, we will build the GovReady-Q application itself.  It is an open source project, and we can pull the source code from the official GitHub repository.  (Or if you prefer, you can clone the official repository into your GitHub account, and use that one.)

* Start at the Jenkins dashboard, at http://localhost:8080/

* Click on “New Item”.

* Enter an item name, such as “GovReady-Q via GitHub”.

* Click “Pipeline” as the type of project, then click “OK” at the bottom of the screen.

* Now, to configure the project, click the “Pipeline” tab to scroll down to the Pipeline section.

* For “Definition”, choose “Pipeline script from SCM”.  This will tell Jenkins to look in the GovReady-Q repository for a Jenkinsfile to use as the pipeline script.

* For “SCM”, choose “Git”.  Then for “Repository URL”, enter the “Clone with HTTPS” URL for the repository, which is “https://github.com/GovReady/govready-q.git”.

* You can leave “Credentials” set to “none”.  (For a private repository, you could set up a GitHub personal access token for Jenkins to use, and then provide it to Jenkins here.)

* TODO. Review target app’s Jenkinsfile.

* Click “Save”, and you’re almostready to build.


#### Provide Compliance Server Credentials

In Jenkins, go to the top level of Jenkins, and then to the Credentials page.

Click on a credential scope, such as the global scope.

Add two `Secret Text` credentials. The first looks like:

![](jenkins-credentials-2.png)

Set the `govready_q_api_url` and `govready_q_api_key` credentials to the URL and API key retreived when setting up the Compliance Server.

Once the credentials have been set, they will look like this:

![](jenkins-credentials-1.png)


### Step 4: Build, Test, and ATO the Application in the Pipeline


#### Review the Jenkinsfile

The target application uses a `Jenkinsfile` to define the build, test, and deployment steps for the application. The `Jenkinsfile` is stored in the **Application Source Code Repository** and will be fetched by Jenkins when a build is initiated.

Some of the important parts of the Jenkins file are described below.

	pipeline {
	  agent {
	    docker {
	      image 'python:3'
	      args '-p 8001:8001 --network continuousato'
	    }
	  }

The `agent` section defines the properties of an ephemeral Docker container that runs the build steps. This is also our **Target Application Server**. The container is added to the virtual network created earlier using `--network continuousato`, which allows the build container to communicate with the **Compliance Server**. Port forwarding is also enabled with `-p` to allow the DevSecOps Engineer to visit the target application when the build completes (TODO: except the container is ephemeral so not really).

	  stages {
	    stage('Build App') {
	      steps {
	        sh 'pip install -r requirements.txt'
	      }
	    }

The build phase contains typical Jenkins build instructions. In this case, we install the target application’s Python package dependencies.

	    stage('Test App') {
	      steps {
	        sh './manage.py test 2>&1 | tee /tmp/pytestresults.txt'

The test stage runs the target application’s tests (unit tests, integration tests, etc.). The Unix `tee` command is used to save the test results to a temporary file while also retaining the console output that is fed to Jenkins.

	        withCredentials([
	        	string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'),
	        	string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {

	            // Send hostname.
	            sh 'curl -F project.file_server.hostname=$(hostname)
	                     --header "Authorization:$Q_API_KEY" $Q_API_URL'

	            // Send test results.
	            sh 'curl -F "project.file_server.login_message=</tmp/pytestresults.txt"
	                     --header "Authorization:$Q_API_KEY" $Q_API_URL'
	        }
	      }
	    }
	  }
	}

The test stage then sends information about the build to the **Compliance Server** using the GovReady-Q Compliance App’s API. `withCredentials` is a Jenkins command that pulls credentials (see above) into environment variables. Within `withCredentials`, two API calls are made:

1. The first API call sends the build machine’s hostname, as returned by the Unix `hostname` command, and stores it in the Compliance App’s `project.file_server.hostname` data field.

2. The second API call sends the saved test results from the temporary file and stores it in the Compliance App’s `project.file_server.login_message` data field. (TODO: Change the field name.)

#### Further Steps (TODO)

* Start the build.
* Watch Jenkins run the build tasks.
* Watch Jenkins run the testing tasks of the application and the security and monitoring server.
* Watch Jenkins share information with the compliance server to update the System Security Plan and ATO.

### Step 5: View Compliance ATO Artifacts

* View the results in the GovReady-Q Compliance Server.

### Step 6: Tear-down

Stop the **Build Server** (Jenkins) container simply by typing CTRL+C into its terminal. The container will be automatically removed. You must also remove its persistent data volume:

	docker volume rm jenkins-data

Remove the **Compliance Server** container using:

	docker container rm -f govready-q

