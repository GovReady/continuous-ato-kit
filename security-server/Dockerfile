# Build on official CentOS 7 image.
FROM centos:7

# Install scan-http-daemon.py
COPY scan-http-daemon.py ./

# Install ssh client.
RUN yum -y install openssh-clients

# Install private key for target app server and disable strict host key check
RUN mkdir /root/.ssh && chmod 700 /root/.ssh
COPY keys/id_ecdsa /root/.ssh/id_ecdsa
RUN chmod 400 /root/.ssh/id_ecdsa
RUN echo "StrictHostKeyChecking no" >/root/.ssh/config

# Run scan daemon.
ENTRYPOINT ["./scan-http-daemon.py", "8045"]
