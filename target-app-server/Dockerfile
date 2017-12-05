# Build on official CentOS 7 image.
FROM centos:7

# Expose the ssh port.
EXPOSE 22

# Install OpenSCAP.
RUN yum install -y openscap-scanner scap-security-guide

# Install sshd and ssh clients.
RUN yum -y update; yum clean all
RUN yum -y install openssh-server openssh-clients
RUN mkdir /var/run/sshd

# Generate the server SSH keys.
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N '' 
RUN ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N '' 
RUN ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N '' 

# Allow public key authentication.
RUN sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Create user.
ENV SSH_USER=target
RUN useradd $SSH_USER

# Install target app server public key
COPY keys/target_ecdsa.pub /home/target/.ssh/authorized_keys
RUN chmod 400 /home/target/.ssh/authorized_keys && chown -R target:target /home/target/.ssh

ENTRYPOINT ["/usr/sbin/sshd", "-D"]
