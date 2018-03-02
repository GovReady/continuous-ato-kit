Notes for our Digital Ocean server
----------------------------------

Open ports to the landing page, Jenkins, and GovReady-Q:

    ufw allow 80 && ufw allow 8080 && ufw allow 8000

Get the kit:

    git clone https://github.com/GovReady/continuous-ato-kit/
    cd continuous-ato-kit/

Change GovReady-Q's hostname from the unqualified default "govready-q" to the fully qualified domain name that points to this machine:

    sed -i s/HOST=govready-q/HOST=continuous-ato-kit.govready.com/ docker-compose.yml

Start the homepage server that also can start/stop the fake FTP process that opens a port on the target application server:

    (cd droplet-notes/; nohup python3 daemon.py;) &

Start the kit:

    ./atokit-up.sh

Get credentials:

    ./get-jenkins-password.sh # log into Jenkins with this
    docker-compose exec govready-q ./first_run.py # log into Q with this, and info to set up Jenkins pipeline too

Continue with the general docker-compose instructions.
