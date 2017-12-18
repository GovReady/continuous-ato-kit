# Adding Continuous ATO into a Build Pipeline

This proof-of-concept demonstrates how security checks, compliance testing, and compliance artifact maintenance can be just another automated part of the Continuous Integration/Continuous Deployment (CI/CD) pipeline.

This document describes how a build pipeline can be constructed using Jenkins to create a Continuous ATO.


## Pipeline Environment

A typical CI/CI build pipeline uses a build server such as Jenkins to download, build, and deploy target application source code to a **Target Application Server**, which, if tests pass, becomes a staging or production environment. In this demonstration, we add new components to the build pipeline:

* A **Security Server** running OpenSCAP and nmap, which performs security scanning on a test environment as an integral part of the build process.
* A **Compliance Server** running [GovReady-Q](https://github.com/GovReady/govready-q), which collects and combines evidence from the build, such as security scan reports, with policy and technical controls to produce compliance artifacts such as a System Security Plan. The compliance server also performs buisness logic rules to support compliance go-no-go decision-making.

The complete build environment is:

![Diagram showing a build pipeline environment consisting of a Source Code Repository (GitHub) a Build Server (Jenkins), a Target Application Instance, a Security and Monitoring Server (OpenSCAP), a Compliance Server (GovReady-Q), a DevSecOps Workstation, and Production Environment.](docs/c-a-k-system-diagram-p1.png)

We use a Jenkinsfile that begins like a typical Jenkinsfile with stages for setting up the operating system, fetching application source code, building the application, and running tests.

In this example, the Jenkinsfile uses a CentOS 7 Docker image for the **Target Application Server**:

	agent {
	  docker {
	    image 'centos:7'
	  }
	}

In addition to the usual stages in the Jenkinsfile, we add additional stages for:

* Preparing the operating system to run OpenSCAP
* Running compliance tests and uploading compliance data and evidence to the Compliance Server


### Adding an OpenSCAP Security Scan

#### What we're modeling

In enterprise environments, security scans of systems are typically launched from security servers run by the security team. As a result, our pipeline models an environment where the scan is launched on a **Security Server** which begins the tests on the **Target Application Server**.

OpenSCAP is a tool to scan a system for security configuration problems. Because OpenSCAP scans the local filesystem and operating system settings, it runs on the machine that is being scanned. As a result, it must be installed on the **Target Application Server**, which Jenkins is building. To model the enterprise workflow, the **Security Server** logs into the **Target Application Server** over SSH, initiates OpenSCAP on the **Target Application Server**, and then saves the scap results in a place Jenkins can access later.

The complete pipeline for the OpenSCAP security scan is:

* The **Security Server** runs an HTTP daemon that listens for requests from servers that want to be scanned.
* The Jenkinsfile initiates a request to the **Security Server** to begin an OpenSCAP scan of the **Target Application Server**.
* The **Security Server** logs into the **Target Application Server** over SSH. The **Security Server**'s public key must be stored on the **Target Application Server** to permit the login.
* In the SSH connection, the **Security Server** begins OpenSCAP and saves the scan results to a temporary file on the **Target Application Server**.

#### Setting up the Jenkinsfile

The SSH connection is made possible by a) installing the OpenSSH server on the **Target Application Server**, b) creating a user on the **Target Application Server** that the **Security Server** will log in as, and c) storing the public key of the **Security Server** in the user's `authorized_keys` file.

We use Jenkins Credentials to hold the **Security Server**'s public key. A "Secret File"-type Credential is created that holds the public key file. The secret is named `target_ecdsa.pub`. The pipeline step `withCredentials` is used to copy the file from Jenkins Credentials onto the **Target Application Server**.

In the `OS Setup` stage of the Jenkinsfile, steps are added to install the OpenSSH server:

    // Install sshd, generate the server SSH keys, and configure sshd to
    // allow login via a public key, then start the daemon.
    sh 'yum install -y openssh-server openssh-clients'
    sh 'mkdir /var/run/sshd'
    sh "ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''"
    sh "ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''"
    sh "ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''"
    sh "sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config"
    sh '/usr/sbin/sshd'

And then to create a user that the **Security Server** can log in as:

    // Create a user for the Security Server to log in as.
    sh 'useradd target && mkdir /home/target/.ssh && chmod 700 /home/target/.ssh'
    
    // Install target app server public key.
    withCredentials([file(credentialsId: 'target_ecdsa.pub', variable: 'TARGET_ECDSA_PUB')]) {
        sh 'mv "$TARGET_ECDSA_PUB" /home/target/.ssh/authorized_keys'
    }
    sh 'chmod 400 /home/target/.ssh/authorized_keys && chown -R target:target /home/target/.ssh'

A step is also added to install OpenSCAP:

    sh 'yum install -y openscap-scanner scap-security-guide'

#### Triggering the scan

We also add a step to the Jenkinsfile to trigger the scan. The **Security Server**'s HTTP daamon is listening for a request for a scan, which the Jenkinsfile can trigger by using `curl`:

    sh 'curl -s http://security-server:8045/oscap'

When the **Security Server** daemon receives the request, it runs:

	ssh target@target-app-server \
	  'oscap xccdf eval --profile nist-800-171-cui --fetch-remote-resources \
	   --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-centos7-xccdf.xml \
	   || oscap xccdf generate report scan-results.xml > /tmp/scan-report.html'

This command connects to the **Target Application Server** to run OpenSCAP, saving the results in XML and the report in HTML to the `/tmp` directory on the **Target Application Server**.

### The compliance stage
