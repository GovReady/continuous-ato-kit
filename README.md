# Continuous ATO Kit

The Continuous ATO Kit is a reference implementation of continuous compliance automation--security checking, compliance testing, and compliance artifact maintenance--in the Continuous Integration/Continuous Deployment (CI/CD) pipeline.

The example scenerio is getting and continuously monitoring an ATO (Authority To Operate) for an IT system at an agency in the federal government under the NIST RMF (Risk Management Framework).

Documentation for this project can be found in the following documents:

1. The Need for Continuous ATO explains why it will be valuable to incorporate the Authority to Operate A&A process into an agile build pipeline.
1. [Example Build Pipeline](Pipeline.md) explains the pipeline constructed in this proof-of-concept, using Jenkins, a security and monitoring server running OpenSCAP and namp, and a compliance server running GovReady-Q.
1. [Try It Using Docker Compose](TryIt.md) is a step-by-step tutorial to running the example build pipeline on your local workstation using docker-compose.
1. Enterprise Deployment Guide is a step-by-step tutorial for deploying our pipeline on bare-metal virtualized servers.
