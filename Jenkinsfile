pipeline {
  agent {
    docker {
      image 'centos:7'
      args '-p 8001:8001 --network continuousato'
    }
  }
  stages {
    stage('OS Setup') {
      steps {
        sh 'yum -y install https://centos7.iuscommunity.org/ius-release.rpm'
        sh 'yum -y install python36u python36u-devel.x86_64 python36u-pip'
      }
    }
    stage('Build') {
      steps {
        sh 'pip3.6 install mondrianish'

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Build%20OK
        // with "'"'s \'s escaped
        echo '. ____        _ _     _    ___  _  __\n | __ ) _   _(_| | __| |  / _ \\| |/ /\n |  _ \\| | | | | |/ _` | | | | | \' / \n | |_) | |_| | | | (_| | | |_| | . \\ \n |____/ \\__,_|_|_|\\__,_|  \\___/|_|\\_\\'
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
        echo '. _____        _         ____               \n |_   ____ ___| |_ ___  |  _ \\ __ _ ___ ___ \n   | |/ _ / __| __/ __| | |_) / _` / __/ __|\n   | |  __\\__ | |_\\__ \\ |  __| (_| \\__ \\__ \\\n   |_|\\___|___/\\__|___/ |_|   \\__,_|___|___/'
      }                                     
    }
    stage('Compliance') {
      steps {
        // Scan system.
        sh 'yum install -y openscap-scanner scap-security-guide elinks'
        sh 'oscap xccdf eval --profile nist-800-171-cui  --fetch-remote-resources --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-centos7-xccdf.xml || true'
        sh 'oscap xccdf generate report scan-results.xml > /tmp/scan-report.html'

        // Send hostname, test results, and scan results to Q.
        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            sh 'curl -s \
              -F "project.file_server.hostname=$(hostname)" \
              -F "project.file_server.login_message=</tmp/pytestresults.txt" \
              -F "project.file_server.scap_scan_report=@/tmp/scan-report.html" \
              --header "Authorization:$Q_API_KEY" $Q_API_URL'
        }

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Compliant
        echo '.   ____                      _ _             _   \n  / ___|___  _ __ ___  _ __ | (_) __ _ _ __ | |_ \n | |   / _ \\| \'_ ` _ \\| \'_ \\| | |/ _` | \'_ \\| __|\n | |__| (_) | | | | | | |_) | | | (_| | | | | |_ \n  \\____\\___/|_| |_| |_| .__/|_|_|\\__,_|_| |_|\\__|\n                      |_|                        '

      }
    }
  }
}