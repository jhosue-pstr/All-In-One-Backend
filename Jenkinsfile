pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    environment {
        SONAR_HOST_URL = 'http://sonarqube:9000'
        SONAR_TOKEN    = credentials('Sonar-qube')
        PROJECT_KEY    = 'All-In-One-Backend'
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
            }
        }

        stage('SonarQube Analysis') {
            steps {
                sh '''docker run --rm \
                    --volumes-from jenkins \
                    --network app-network \
                    -e SONAR_TOKEN="${SONAR_TOKEN}" \
                    sonarsource/sonar-scanner-cli:latest \
                    -Dsonar.projectKey=${PROJECT_KEY} \
                    -Dsonar.projectBaseDir=${WORKSPACE} \
                    -Dsonar.sources=app \
                    -Dsonar.tests=test \
                    -Dsonar.exclusions=test/**,media/**,*.db \
                    -Dsonar.python.coverage.reportPaths=coverage.xml \
                    -Dsonar.python.version=3.12 \
                    -Dsonar.host.url=${SONAR_HOST_URL}'''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t all-in-one-backend:latest .'
            }
        }
    }

    post {
        always {
            script {
                node {
                    sh 'rm -rf venv/ .pytest_cache __pycache__ .coverage coverage.xml test.db'
                    deleteDir()
                }
            }
        }
        success {
            echo 'Pipeline completado exitosamente'
        }
        failure {
            echo 'Pipeline falló'
        }
    }
}
