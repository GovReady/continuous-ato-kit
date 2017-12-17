# Adding Continuous ATO into a Build Pipeline

A typical build pipeline uses a build server such as Jenkins to download, build, and deploy target application source code to a testing or production environment. In this demonstration, we add new components to the build pipeline:

* A **Security Server** running OpenSCAP and nmap, which will perform security scanning on a test environment as an integral part of the build process.
* A **GovReady-Q Compliance Server**, which collects and combines evidence from the build, such as security scan reports, with policy and technical controls to produce compliance artifacts such as a System Security Plan.

The complete build environment is:

![Diagram showing a build pipeline environment consisting of a Source Code Repository (GitHub) a Build Server (Jenkins), a Target Application Instance, a Security and Monitoring Server (OpenSCAP), a Compliance Server (GovReady-Q), a DevSecOps Workstation, and Production Environment.](docs/c-a-k-system-diagram-p1.png)


