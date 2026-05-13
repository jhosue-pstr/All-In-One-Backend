pipeline {
    agent any

    environment {
        SONAR_HOST_URL = 'https://sonarcloud.io'
        SONAR_TOKEN    = credentials('sonar-token')
        PROJECT_KEY    = 'jhosue-pstr_All-In-One-Backend'
        ORG            = 'jhosue-pstr'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '. venv/bin/activate && pip install -r requirements.txt'
                sh '. venv/bin/activate && pip install pytest pytest-cov'
            }
        }

        stage('Run Tests') {
            steps {
                sh '. venv/bin/activate && pytest --cov=app --cov-report=xml --cov-report=term'
                sh "sed -i 's|$WORKSPACE|.|g' coverage.xml"
            }
        }

        stage('SonarCloud Analysis') {
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh '''sonar-scanner \
                        -Dsonar.projectKey=${PROJECT_KEY} \
                        -Dsonar.organization=${ORG} \
                        -Dsonar.sources=app \
                        -Dsonar.tests=test \
                        -Dsonar.exclusions=media/**,*.db \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.python.version=3.12'''
                }
            }
        }

        // CNES REPORT - Deshabilitado por incompatibilidad con SonarCloud API v8
        // Revisar: https://github.com/cnescatlab/sonar-cnes-report/releases
        // stage('Generate CNES Report') {
        //     steps {
        //         sh 'curl -sL -o sonar-cnes-report.jar "https://github.com/cnescatlab/sonar-cnes-report/releases/download/5.0.4/sonar-cnes-report-5.0.4.jar"'
        //         sh 'java -jar sonar-cnes-report.jar -t ${SONAR_TOKEN} -s ${SONAR_HOST_URL} -p ${PROJECT_KEY} -o ./cnes-report'
        //     }
        // }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t all-in-one-backend:latest .'
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
