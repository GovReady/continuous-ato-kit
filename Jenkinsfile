pipeline {
  agent {
    docker {
      image 'centos:7'
      args '--network continuousatokit_ato_network --name target-app-server'
    }
  }
  stages {
    stage('OS Setup') {
      steps {
        // Move the yum cache to the workspace directly because it's persisted
        // by Jenkins and makes builds (after the first build) faster.
        sh 'mkdir -p .yum'
        sh 'if [ ! -L /var/cache/yum ]; then \
          rm -rf /var/cache/yum; \
          ln -s "`pwd`/.yum" /var/cache/yum; \
          fi'

        // Install packages required to build the application.
        sh 'yum -y install https://centos7.iuscommunity.org/ius-release.rpm'
        sh 'yum -y install python36u python36u-devel.x86_64 python36u-pip'

        // Install packages required to allow the Security and Monitoring Server
        // to log into this container and run OpenSCAP.
        //
        // Install OpenSCAP.
        sh 'yum install -y openscap-scanner scap-security-guide'
        //
        // Install sshd, generate the server SSH keys, and configure sshd to
        // allow login via a public key:
        sh 'yum install -y openssh-server openssh-clients'
        sh 'mkdir /var/run/sshd'
        sh "ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key -N ''"
        sh "ssh-keygen -t ecdsa -f /etc/ssh/ssh_host_ecdsa_key -N ''"
        sh "ssh-keygen -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -N ''"
        sh "sed -i 's/^#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config"
        //
        // Create a user for the other server to log in as.
        sh 'useradd target && mkdir /home/target/.ssh && chmod 700 /home/target/.ssh'
        //
        // Install target app server public key.
        withCredentials([file(credentialsId: 'target_ecdsa.pub', variable: 'TARGET_ECDSA_PUB')]) {
            sh 'mv "$TARGET_ECDSA_PUB" /home/target/.ssh/authorized_keys'
        }
        sh 'chmod 400 /home/target/.ssh/authorized_keys && chown -R target:target /home/target/.ssh'
        //
        // Start sshd daemon in the background.
        sh '/usr/sbin/sshd'
      }
    }
    stage('Build') {
      steps {
        sh 'pip3.6 install mondrianish'

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Build%20OK
        // with "'"'s \'s escaped
        writeFile file:"ascii.txt", text:'. ____        _ _     _    ___  _  __\n | __ ) _   _(_| | __| |  / _ \\| |/ /\n |  _ \\| | | | | |/ _` | | | | | \' / \n | |_) | |_| | | | (_| | | |_| | . \\ \n |____/ \\__,_|_|_|\\__,_|  \\___/|_|\\_\\\n'
        sh 'cat ascii.txt && sleep 4'
        //input 'Ready to Test?'
      }
    }
    stage('Test') {
      steps {
        // Run the application.
        sh 'LANG=en_US.UTF-8 mondrianish --size 20x10 text'

        // Run python unit tests.
        sh 'python tests.py 2>&1 | tee /tmp/pytestresults.txt'
        sh 'sed -i s/$/\\\\\\\\/ /tmp/pytestresults.txt'
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Tests%20Pass
        writeFile file:"ascii.txt", text:'. _____        _         ____               \n |_   ____ ___| |_ ___  |  _ \\ __ _ ___ ___ \n   | |/ _ / __| __/ __| | |_) / _` / __/ __|\n   | |  __\\__ | |_\\__ \\ |  __| (_| \\__ \\__ \\\n   |_|\\___|___/\\__|___/ |_|   \\__,_|___|___/\n'
        sh 'cat ascii.txt && sleep 4'
      }                                     
    }
    stage('Compliance') {
      steps {
        // Ask the Security Monitoring Server to scan this system.
        sh 'curl -s http://security-server:8045/oscap'
        sh 'curl -s http://security-server:8045/port-scan > /tmp/port-scan-output.txt'

        // Send hostname, test results, and scan results to Q.
        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            sh 'curl -s \
              -F "project.file_server.hostname=$(hostname)" \
              -F "project.file_server.login_message=</tmp/pytestresults.txt" \
              -F "project.file_server.scap_scan_report=@/tmp/scan-report.html" \
              -F "project.file_server.port_scan_output=</tmp/port-scan-output.txt" \
              -F "project.file_server.port_scan_ok=`if grep -q ^21/tcp /tmp/port-scan-output.txt; then echo no; else echo yes ; fi`" \
              --header "Authorization:$Q_API_KEY" $Q_API_URL'
        }

        // Break build if port scan was not compliant
        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Out%20Of%20Compliance
        // (', \, and newlines escaped)
        writeFile file:"ascii.txt", text:'   ___        _      ___   __    ____                      _ _                      \n  / _ \\ _   _| |_   / _ \\ / _|  / ___|___  _ __ ___  _ __ | (_) __ _ _ __   ___ ___ \n | | | | | | | __| | | | | |_  | |   / _ \\| \'_ ` _ \\| \'_ \\| | |/ _` | \'_ \\ / __/ _ \\\n | |_| | |_| | |_  | |_| |  _| | |__| (_) | | | | | | |_) | | | (_| | | | | (_|  __/\n  \\___/ \\__,_|\\__|  \\___/|_|    \\____\\___/|_| |_| |_| .__/|_|_|\\__,_|_| |_|\\___\\___|\n                                                    |_|                             '
        sh 'if grep -q ^21/tcp /tmp/port-scan-output.txt; then \
          cat ascii.txt && sleep 4; \
          exit 1; \
        fi'


        echo 'System is compliant.'

        echo 'Notifications sent to information system security officer.'

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Compliant
        writeFile file:"ascii.txt", text:'.  ____                      _ _             _   \n  / ___|___  _ __ ___  _ __ | (_) __ _ _ __ | |_ \n | |   / _ \\| \'_ ` _ \\| \'_ \\| | |/ _` | \'_ \\| __|\n | |__| (_) | | | | | | |_) | | | (_| | | | | |_ \n  \\____\\___/|_| |_| |_| .__/|_|_|\\__,_|_| |_|\\__|\n                      |_|                     \n'
        sh 'cat ascii.txt && sleep 4'

      }
    }
  }
}