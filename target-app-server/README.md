# govready/centos7-cak1-baseline

This directory is used by GovReady engineers to build the `centos7-cak1-baseline` image and push it to Docker Hub.  The image is pulled from Docker Hub to your computer, and used by the main [Jenkinsfile](../Jenkinsfile) to instantiate the **Target App Server**.

## Build `centos7-cak1-baseline` Image
```
docker build --tag govready/centos7-cak1-baseline:latest .
```

## Push to Docker Hub
```
docker push govready/centos7-cak1-baseline:latest
```
