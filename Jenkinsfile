pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    environment {
        SONAR_HOST_URL = 'http://sonarqube:9000'
        SONAR_TOKEN    = credentials('Sonar-qube')
        PROJECT_KEY    = 'All-In-One-Backend'
        DOCKER_COMPOSE = "${WORKSPACE}/bin/docker-compose"
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

        stage('Build Docker Images') {
            steps {
                sh 'docker build -t all-in-one-backend:latest .'
                sh 'docker build -t k6-tests:latest -f Dockerfile.k6-tests .'
                sh 'docker build -t zap-tester:latest -f zap/Dockerfile ./zap'
                sh 'docker build -t grafana-custom:latest -f Dockerfile.grafana .'
            }
        }

        stage('Setup Performance Infra') {
            steps {
                sh '''mkdir -p bin
curl -sL "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o bin/docker-compose
chmod +x bin/docker-compose'''
                sh '${DOCKER_COMPOSE} -p k6 -f docker-compose.k6.yml up -d influxdb grafana'
            }
        }

//         stage('Performance & Security') {
//             parallel {
//                 stage('K6 Load Tests') {
//                     steps {
//                         // sh 'docker run --rm --add-host host.docker.internal:host-gateway -e K6_OUT=influxdb=http://host.docker.internal:8086/k6 -e BASE_URL=http://host.docker.internal:8000 k6-tests:latest run /scripts/tests/01_smoke_test.js || true'
//                         // sh 'docker run --rm --add-host host.docker.internal:host-gateway -e K6_OUT=influxdb=http://host.docker.internal:8086/k6 -e BASE_URL=http://host.docker.internal:8000 k6-tests:latest run /scripts/tests/02_load_test.js || true'
//                         // sh 'docker run --rm --add-host host.docker.internal:host-gateway -e K6_OUT=influxdb=http://host.docker.internal:8086/k6 -e BASE_URL=http://host.docker.internal:8000 k6-tests:latest run /scripts/tests/03_stress_test.js || true'
//                         // sh 'docker run --rm --add-host host.docker.internal:host-gateway -e K6_OUT=influxdb=http://host.docker.internal:8086/k6 -e BASE_URL=http://host.docker.internal:8000 k6-tests:latest run /scripts/tests/04_spike_test.js || true'
//                         // sh 'docker run --rm --add-host host.docker.internal:host-gateway -e K6_OUT=influxdb=http://host.docker.internal:8086/k6 -e BASE_URL=http://host.docker.internal:8000 k6-tests:latest run /scripts/tests/05_soak_test.js || true'
//                     }
//                 }
//                 stage('ZAP Security Scan') {
//                     steps {
//                         script {
//                             parallel(
//                                 baseline: {
//                                     sh '${DOCKER_COMPOSE} -p zap -f docker-compose.zap.yml run --rm baseline || true'
//                                 },
//                                 fullscan: {
//                                     sh '${DOCKER_COMPOSE} -p zap -f docker-compose.zap.yml run --rm fullscan || true'
//                                 },
//                                 apiscan: {
//                                     sh '${DOCKER_COMPOSE} -p zap -f docker-compose.zap.yml run --rm apiscan || true'
//                                 },
//                                 tester: {
//                                     sh '''mkdir -p ./zap/reportes
// docker run --add-host host.docker.internal:host-gateway --name zap-tester-payload -e TARGET_URL=http://host.docker.internal:8000 zap-tester:latest || true
// docker cp zap-tester-payload:/zap/wrk/payload-report.html ./zap/reportes/ 2>/dev/null || true
// docker cp zap-tester-payload:/zap/wrk/payload-report.json ./zap/reportes/ 2>/dev/null || true
// docker rm zap-tester-payload 2>/dev/null || true'''
//                                 }
//                             )
//                         }
//                     }
//                 }
//             }
//         }
    }

    post {
        always {
            sh 'docker ps -q --filter "label=com.docker.compose.project=zap" | xargs -r docker rm -f 2>/dev/null || true'
            sh 'rm -rf venv/ .pytest_cache __pycache__ .coverage coverage.xml test.db bin/'
            deleteDir()
        }
        success {
            echo 'Pipeline completado exitosamente'
        }
        failure {
            echo 'Pipeline falló'
        }
    }
}
