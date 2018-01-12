# The Need for Continuous ATO

Federal IT projects are embracing the use of rapid iterations --- the hallmark of the agile development method --- to reduce costs and achieve goals sooner. The Continuous Integration/Continuous Development (CI/CD) agile strategy, in which a complete development-build-deploy cycle is performed once or many times in every iteration, has reduced risks and costs by surfacing mistakes earlier in the software development lifecycle.

Agile has brought many benefits to federal IT projects --- until projects are faced with getting an Authority To Operate. While development and operations have seen the benefits of the agile method, cybersecurity compliance within the NIST Risk Management Framework is still conducted under the old, costly, and high-risk waterfall method.

The Continuous ATO Kit, this project, is a reference implementation of extending agile from development and operations to the security and compliance aspects of federal IT projects. The kit demonstrates security checking, compliance testing, and compliance artifact maintenance in the CI/CI pipeline.

## The Problem

...

Agile methodology reveals two opportunities for federal IT cybersecurity:

* Team members are not communicating well. Engineers consider compliance, if not security, someone else's problem. Compliance officers are seen as the people who say no.
* Decision points can be reached earlier to reduce risk by surfacing and solving problems before it becomes expensive to go back and re-do earlier work.

...

## The Solution

CI/CD pipelines are used to create rapid and repeatable build-test-deploy processes that can be run once or many times within a team iteration. Because they are rapid and repeatable, team members can test the system at any time in a virtual production environment. This allows team members to discover problems in the system that without a CI/CD pipeline would only be discovered later in the software development lifecycle. The earlier a problem is discovered, the better and cheaper its resolution will be. CI/CD pipelines are also used to create build artifacts to remove the possibility of human error when green-lighting the final product.

A typical CI/CI build pipeline uses a build server such as Jenkins to download, build, and deploy target application source code to a **Target Application Server**, which, if tests pass, becomes a staging or production environment. In this demonstration, we add new components to the build pipeline:

* A **Security Server** running OpenSCAP and nmap, which performs security scanning on a test environment as an integral part of the build process.
* A **Compliance Server** running [GovReady-Q](https://github.com/GovReady/govready-q), which collects and combines evidence from the build, such as security scan reports, with policy and technical controls to produce compliance artifacts such as a System Security Plan. The compliance server also performs buisness logic rules to support compliance go-no-go decision-making.

The complete build environment is:

![Diagram showing a build pipeline environment consisting of a Source Code Repository (GitHub) a Build Server (Jenkins), a Target Application Instance, a Security and Monitoring Server (OpenSCAP), a Compliance Server (GovReady-Q), a DevSecOps Workstation, and Production Environment.](docs/c-a-k-system-diagram-p1.png)

As in traditional CI/CI pipelines, each step is an opportunity to check the system: Did the source code build correctly? Did unit tests pass? Did deployment (to the test environment) succeed? Do functional tests on the deployed system pass? By adding security and compliance to the build process, the CI/CI pipeline becomes an opportunity to check the system for security and compliance issues:

* Do security tests pass? Is the system secure?
* Is system configuration consistent with organization policy? Do business logic rules for compliance pass?

When the CI/CD pipeline answers these questions in the negative, that is, when there is a failure, the pipeline knows that a decision point has been reached:

* Security and compliance team members can be notified.
* Deployment to production can be automatically halted.
* A discussion between development, operations, security, and compliance can begin.

In addition, the CI/CD pipeline can be used to generate build artifacts, such as:

* a System Security Plan
* Evidence of compliance, such as the output of a port scan
* Plans of Action and Milestones (POAMs) based on the gap between organizational requirements as the system's actional state

This pipeline addresses both opportunities identified earlier:

* GovReady-Q provides a place for team members to communicate with each other about security and compliance tasks related to the IT project.
* Decision points are reached earlier because team members can run the security and compliance steps at any time during the software development lifecycle.
