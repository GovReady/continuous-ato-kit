pipeline {
  agent {
    docker {
      image 'python:3'
      args '-p 8000:8000'
    }
  }
  stages {
    //stage('OS Setup') {
    //  steps {
    //    sh 'apt-get update && apt-get install -y unzip && apt-get clean'
    //  }
    //}
    stage('Build App') {
      steps {
        sh 'pip install mondrianish'
      }
    }
    stage('Test App') {
      steps {
        sh 'mondrianish --size 20x10 text | tee /tmp/pytestresults.txt'

        sh 'python tests.py 2>&1 | tee /tmp/pytestresults.txt'
        sh 'sed -i s/$/\\\\\\\\/ /tmp/pytestresults.txt'
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break
        sh 'echo >> /tmp/pytestresults.txt' // add blank line because trailing \ is not valid as a hard break

        withCredentials([string(credentialsId: 'govready_q_api_url', variable: 'Q_API_URL'), string(credentialsId: 'govready_q_api_key', variable: 'Q_API_KEY')]) {
            // Send hostname.
            sh 'curl -F project.file_server.hostname=$(hostname) --header "Authorization:$Q_API_KEY" $Q_API_URL'

            // Send test results.
            sh 'curl -F "project.file_server.login_message=</tmp/pytestresults.txt" --header "Authorization:$Q_API_KEY" $Q_API_URL'
        }

      }
    }
  }
}