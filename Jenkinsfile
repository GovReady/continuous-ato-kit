pipeline {
  agent {
    docker {
      image 'python:3'
      args '-p 8001:8001 --network continuousato'
    }
  }
  stages {
    //stage('OS Setup') {
    //  steps {
    //    sh 'apt-get update && apt-get install -y unzip && apt-get clean'
    //  }
    //}
    stage('Build') {
      steps {
        sh 'pip install mondrianish'

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Build%20OK
        // with "'"'s \'s escaped
        echo '  ____        _ _     _    ___  _  __\n | __ ) _   _(_| | __| |  / _ \\| |/ /\n |  _ \\| | | | | |/ _` | | | | | \' / \n | |_) | |_| | | | (_| | | |_| | . \\ \n |____/ \\__,_|_|_|\\__,_|  \\___/|_|\\_\\'
      }
    }
    stage('Test') {
      steps {
        sh 'mondrianish --size 20x10 text | tee /tmp/pytestresults.txt'

        sh 'python tests.py 2>&1 | tee /tmp/pytestresults.txt'
        sh 'sed -i s/$/\\\\\\\\/ /tmp/pytestresults.txt'
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Tests%20Pass
        echo '  _____        _         ____               \n |_   ____ ___| |_ ___  |  _ \\ __ _ ___ ___ \n   | |/ _ / __| __/ __| | |_) / _` / __/ __|\n   | |  __\\__ | |_\\__ \\ |  __| (_| \\__ \\__ \\\n   |_|\\___|___/\\__|___/ |_|   \\__,_|___|___/'
      }                                     
    }
    stage('Compliance') {
      steps {
        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            // Send hostname.
            sh 'curl -s -F project.file_server.hostname=$(hostname) --header "Authorization:$Q_API_KEY" $Q_API_URL'

            // Send test results.
            sh 'curl -s -F "project.file_server.login_message=</tmp/pytestresults.txt" --header "Authorization:$Q_API_KEY" $Q_API_URL'
        }

        // http://www.patorjk.com/software/taag/#p=display&h=3&v=2&f=Standard&t=Compliant
        echo '   ____                      _ _             _   \n  / ___|___  _ __ ___  _ __ | (_) __ _ _ __ | |_ \n | |   / _ \\| \'_ ` _ \\| \'_ \\| | |/ _` | \'_ \\| __|\n | |__| (_) | | | | | | |_) | | | (_| | | | | |_ \n  \\____\\___/|_| |_| |_| .__/|_|_|\\__,_|_| |_|\\__|\n                      |_|                        '

      }
    }
  }
}