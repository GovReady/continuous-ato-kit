# Running This Kit On Separated Machines

You can set this demo up on separated machines (VMs at a hosting provider, physical servers, etc.) instead of Docker containers.

Follow the general server setup specified in `docker-compose.yml` to set up your machines.

The following pre-modified files should also help you get started.  They remove some of the configuration we used specifically for the Docker container constellation the demo creates.

```
Jenkinsfile.separated
security-server/scan-http-daemon.py.separated
security-server/keys/config.separated
```

Described below is how to use them in your servers.  First, we'll create a public/private key pair, because you do not want to use the insecure key pair included in this repo.

### Create A Key Pair For Access To The Ephemeral Target App Server

The **Target App Server** will still be created and run by Jenkins as a Docker container, within the machine that runs Jenkins.  A public key will be installed on the **Target App Server**; you will install the private key on your **Security and Monitoring Server**.

Run ssh-keygen in a temporary directory on your computer:

```
ssh-keygen -t ecdsa -b 521 -N '' -f target_ecdsa
```

You will end up with two files, `target_ecdsa` and `target_ecdsa.pub`.

### Configure Your Security and Monitoring Server

Copy the `target_ecdsa` file from the previous step and `security-server/keys/config.separated` from this repo into the `~/.ssh` directory on your **Security and Monitoring Server**.  Rename the config file to `config` and replace `build.example.net` in it with the hostname of your **Build Server**.

Copy `security-server/scan-http-daemon.py.separated`from this repo to your **Security and Monitoring Server**.  Call it `security-server/scan-http-daemon.py` and make sure it is executable.  Use some method of running and keeping it running.  Running it in a `screen` session is an easy solution while you're prototyping.  You may wish to use something more permanent that starts it during server startup, and re-runs it if it exits unexpectedly.  (Add some more examples here.)

The `nmap` port scan in the separated version removes the `-p-` and `-sT` flags; they work with the Docker containers and Docker network, but the more conservative default options might be better on your network.  Go ahead and tweak as appropriate for your network.

### Configure Jenkins

* Click "Configure".
* Click "Pipeline".
* For "Definition", select "Pipeline script" (instead of "Pipeline script from SCM").
* Copy and paste the content of `Jenkinsfile.separated` into the text box.
* Replace the two instances of `security.example.net`with the hostname of your **Security and Monitoring Server**.
* When setting up the credentials, use the `target_ecdsa.pub` file you created above, instead of the file included in the repo.
