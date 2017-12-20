# Baseline Image for Continuous ATO Kit

This directory is used by GovReady engineers to build the `centos7-cak1-baseline` image and push it to Docker Hub.  The image is pulled from Docker Hub to your computer, and used by the main [Jenkinsfile](../Jenkinsfile) to instantiate the container for the **Target App Server**.

We've included this directory so you can see how the base image used in the demo is put together, and we also have discussion below of things we ran into as we put it together.

## Resolving OpenSCAP Scan Issues

The general topic of resolving OpenSCAP issues in any environment, and particularly production, is complex, and should be done in collaboration with your Information System Security Officer (ISSO).  A deep dive into the topic is out of scope for this demo kit.

We had these goals and motivations:

* Favor demo-ability over actual hardening -- after all this is a demo, not a production deployment.
* Have an executive demo that flows quickly and smoothly and simulates a 100% green scan result.
* Fixing all scan configuration issues due to running within a Docker Community Edition container is out of scope.

We took two approaches:

1. Remediate what we could easily remediate.

2. Disable still-failing OpenSCAP rules.  We do not recommend this approach for production deployments; again, you will need to collaborate with your ISSO to best bring your systems into compliance.

For remediation, check what we've done in the [Dockerfile](Dockerfile) in these sections:

* We run `fix.sh`: This auto-generated script is created with the `oscap generate fix` command, and then we run it as part of building the image.
* Additional Remediations: These are commands we run after `fix.sh` based on examining the out-of-compliance system and crafting command lines that will clear the fault.

Then, for the image we're building, failing OpenSCAP rules appear to fall into several classes:

* Intrinsic failures.  A good example is `installed_OS_is_certified`.  We wanted to make this kit distributable, so our OS is not certified, and cannot be made to be certified.
* `yum install` failures.  An apparent bug in the yum configuration of the server causes some of the `fix.sh` commands to fail with `.../ius/stable/CentOS/7/x86_64/repodata/repomd.xml.asc: [Errno 14] HTTP Error 404 - Not Found`, so some rules that might be remediated by `fix.sh` are not.  When we fix the yum configuration, this class will disappear.
* `systemctl` failures.  Some of the rules want to start services with `systemctl`.  The `systemd` subsystem doesn't run in non-privileged Docker containers, so these rules are not easy to remediate.  We are looking into running `systemd` within the container, but this class needs more investigation to resolve.
* Potentially broken tests.  During development, we saw some rules that still failed, despite have been remediated.  This class needs more investigation.
* The rest, which we haven't classified.

Another set of rules just take a while to scan, so our goal of the demo flowing quickly and smoothly is not satisfied if we enable them.

For all of these rules, we took the approach of de-selecting them in the OpenSCAP profile.  This is done with an unsophisticated `awk` command which looks for the id of the rule, and changes `selected="true"` to `selected="false"`.

These are rules we've deselected this way are listed in separate text files, which are then processed by the `awk` command:

* `disable-high.txt` - high priority rules
* `disable-medium.txt` - medium priority rules
* `disable-low.txt` - low priority rules
* `disable-slow.txt` - rules that scan slowly
* `disable-sshd.txt` - rules involving `sshd_config`, segregated because we can remediate these in one config file, when we have time to take the ticket

Remember, this section describes how we approached remediation and deselection for this demonstration kit.  We do not recommend this approach for production deployments; please work with your ISSO as you bring your systems into compliance.

## Baseline Image Development Workflow

This shows a typical modify+debug cycle while working on the image.  The container name and image tag used in this example is "dev003"; it could be whatever, and might be the name of the current `git` branch, for instance.

```
# make sure any previous container is stopped
docker stop dev003

# build the dev image
docker build --tag govready/centos7-cak1-baseline:dev003 .

# run the image, then "exec" an OpenSCAP scan
docker run --rm -d --name dev003 govready/centos7-cak1-baseline:dev003
docker exec dev003 oscap xccdf eval --profile nist-800-171-cui  --fetch-remote-resources --results scan-results.xml --report scan-report.html /usr/share/xml/scap/ssg/content/ssg-centos7-xccdf.xml

# retrieve the results (HTML here, could also be "scan-results.xml" or whatever)
docker exec dev003 cat /scan-report.html >tmp.html

# now examine tmp.html in local web browser

# or check things out via bash, within the running container
docker exec -it dev003 bash

# make changes, the start again at the top

# when done, build the release and push
docker build --tag govready/centos7-cak1-baseline:latest .
docker push govready/centos7-cak1-baseline:latest
```

## Creating fix.sh

This script is a concatentation of remediation snippets automatically generated by OpenSCAP.  We use this to apply remediations to the image we're building.  It's not perfect, but it does effect some remediations.

It is generated with these commands, run inside a container with OpenSCAP installed, and needing fixes:

```
oscap xccdf eval --profile nist-800-171-cui  --fetch-remote-resources --results scan-results.xml --report scan-report.html /usr/share/xml/scap/ssg/content/ssg-centos7-xccdf.xml
oscap xccdf generate fix --fetch-remote-resources --result-id xccdf_org.open-scap_testresult_nist-800-171-cui scan-results.xml > fix.sh
```

After it's generated, copy it out of the container and into your copy of the repo directory (customize the `docker exec` command with the name of your container, and the directory within the container where you generated the `fix.sh` file):

```
cp fix-sh-preamble.txt fix.sh
docker exec -it tmp-cak1-baseline cat /fix.sh >>fix.sh
chmod +x fix.sh
```

If you are on a Unix-based system, you may need to remove carriage return characters from `fix.sh` with something like `tr -d '\r'` or `sed 's/\r//'`.

