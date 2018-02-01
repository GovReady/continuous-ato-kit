pipeline {
  agent {
    docker {
      image 'govready/centos7-cak1-baseline'
      args '--network continuousatokit_ato_network --name target-app-server'
    }
  }
  stages {
    stage('OS Setup') {
      steps {
        // Uncomment this section if you need to install any packages for the target
        // application that aren't alredy installed in the base image
        //
        // // Move the yum cache to the workspace directly because it's persisted
        // // by Jenkins and makes builds (after the first build) faster.
        // sh 'mkdir -p .yum'
        // sh 'if [ ! -L /var/cache/yum ]; then \
        //   rm -rf /var/cache/yum; \
        //   ln -s "`pwd`/.yum" /var/cache/yum; \
        //   fi'
        //
        // // Install packages required to build the application.
        // sh 'yum -y install https://centos7.iuscommunity.org/ius-release.rpm'
        // sh 'yum -y install git python36u python36u-devel.x86_64 python36u-pip'

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
        // Get application source code.
        sh 'rm -rf mondrianish'
        sh 'git clone https://github.com/GovReady/mondrianish'

        // Build the library.
        sh 'cd mondrianish && pip3.6 install -r requirements.txt'
        sh 'cd mondrianish && python3.6 setup.py build'

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
        sh 'cd mondrianish && LANG=en_US.UTF-8 python3.6 mondrianish/__init__.py --size 40x12 text'

        // Run python unit tests.
        sh 'cd mondrianish && python3.6 test.py 2>&1 | tee /tmp/pytestresults.txt'
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
        sh 'curl http://security-server:8045/oscap'
        sh 'head /tmp/scan-report.html'

        sh 'curl -Ss http://security-server:8045/port-scan > /tmp/port-scan-output.txt'

        // Send hostname, test results, and scan results to Q.
        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            sh 'curl --progress-bar \
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