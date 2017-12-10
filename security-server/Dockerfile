# Build on official CentOS 7 image.

# if FROM image is changed, also change atokit-update.sh
FROM centos:7

# Install scan-http-daemon.py
COPY scan-http-daemon.py ./

# Install ssh client and nmap.
RUN yum -y install openssh-clients nmap

# Install private key for target app server and disable strict host key check
RUN mkdir /root/.ssh && chmod 700 /root/.ssh
COPY keys/id_ecdsa /root/.ssh/id_ecdsa
RUN chmod 400 /root/.ssh/id_ecdsa
RUN echo "StrictHostKeyChecking no" >/root/.ssh/config

# Run scan daemon.
ENTRYPOINT ["./scan-http-daemon.py", "8045"]
