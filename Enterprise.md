# Enterprise Deployment Guide

In an enterprise environment, physical servers or long-lasting virtual machines are more likely to be used for a build pipeline (than Docker containers, which we used in our [main deployment example](TryIt.md)). This demo can be set up on separated machines as well, instead of Docker containers, to model an enterprise deployment pipeline.

## The Servers

As in our [Docker container configuration](TryIt.md), the enterprise pipeline environment consists of:

* A **Build Server** running Jenkins
* A **Security Server** running OpenSCAP and nmap
* A **Compliance Server** running [GovReady-Q](https://github.com/GovReady/govready-q)

### The Build Server

We leave it to you to install Jenkins on the **Build Server**. We have found it convenient to start Jenkins using Docker, e.g. with the following command:

	docker run --name jenkins --rm -u root \
	  -v jenkins-data:/var/jenkins_home \
	  -v /var/run/docker.sock:/var/run/docker.sock \
	  jenkinsci/blueocean

However, you can install Jenkins in the manner most familiar to you.

### The Security Server

In our demonstration, the Security Server is a CentOS 7 machine running a small daemon that performs security scans on other machines at the request of other machines.

On your security server, install Python and nmap, and place [security-server/scan-http-daemon.py](security-server/scan-http-daemon.py) onto the server. Edit the script to modify the `ssh` and `nmap` commands as appropriate to scan the target application running on the **Build Server**.

---

The following pre-modified files should also help you get started.  They remove some of the configuration we used specifically for the Docker container constellation the demo creates.

```
Jenkinsfile.separated
security-server/scan-http-daemon.py.separated
security-server/keys/config.separated
```

Described below is how to use them in your servers.  First, we'll create a public/private key pair, because you do not want to use the insecure key pair included in this repo.

### Create A Key Pair For Access To The Ephemeral Target App Server

The **Target App Server** will still be created and run by Jenkins as a Docker container, within the machine that runs Jenkins.  A public key will be installed on the **Target App Server**; you will install the private key on your **Security and Monitoring Server**.

Run ssh-keygen in a temporary directory on your computer:

```
ssh-keygen -t ecdsa -b 521 -N '' -f target_ecdsa
```

You will end up with two files, `target_ecdsa` and `target_ecdsa.pub`.

### Configure Your Security and Monitoring Server

Copy the `target_ecdsa` file from the previous step and `security-server/keys/config.separated` from this repo into the `~/.ssh` directory on your **Security and Monitoring Server**.  Rename the config file to `config` and replace `build.example.net` in it with the hostname of your **Build Server**.

Copy `security-server/scan-http-daemon.py.separated`from this repo to your **Security and Monitoring Server**.  Call it `security-server/scan-http-daemon.py` and make sure it is executable.  Use some method of running and keeping it running.  Running it in a `screen` session is an easy solution while you're prototyping.  You may wish to use something more permanent that starts it during server startup, and re-runs it if it exits unexpectedly.  (Add some more examples here.)

The `nmap` port scan in the separated version removes the `-p-` and `-sT` flags; they work with the Docker containers and Docker network, but the more conservative default options might be better on your network.  Go ahead and tweak as appropriate for your network.

### Configure Jenkins

* Click "Configure".
* Click "Pipeline".
* For "Definition", select "Pipeline script" (instead of "Pipeline script from SCM").
* Copy and paste the content of `Jenkinsfile.separated` into the text box.
* Replace the two instances of `security.example.net`with the hostname of your **Security and Monitoring Server**.
* When setting up the credentials, use the `target_ecdsa.pub` file you created above, instead of the file included in the repo.

### Breaking the Build

To demonstrate a compliance failure, log into the Jenkins server and run:

	firewall-cmd --zone=public --add-port=21/tcp --permanent
	firewall-cmd --reload

to open port 21 in the software firewall. The open port will fail a business logic rule in the compliance stage of the Jenkinsfile.

To have the build succeed again, close the port:

	firewall-cmd --zone=public --remove-port=21/tcp --permanent
	firewall-cmd --reload

To check whether the port is open:

	firewall-cmd --list-all
