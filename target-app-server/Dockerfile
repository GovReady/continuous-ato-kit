# Build on official CentOS 7 image.
FROM centos:7

# Expose the ssh port.
EXPOSE 22

# Install packages required to build the application.
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install python36u python36u-devel.x86_64 python36u-pip

# Install packages required to allow the Security and Monitoring Server
# to log into this container and run OpenSCAP.

# Install OpenSCAP.
RUN yum install -y openscap-scanner scap-security-guide

# Install sshd and ssh clients.
RUN yum -y install openssh-server openssh-clients
RUN mkdir /var/run/sshd

# Generate SSH keys.
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N '' 
RUN ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N '' 
RUN ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N '' 
RUN sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

# Create a user for the other server to log in as.
RUN useradd target && mkdir /home/target/.ssh && chmod 700 /home/target/.ssh

# start a null process
CMD ["/usr/sbin/init"]
