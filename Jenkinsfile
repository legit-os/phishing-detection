pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'phishing-detection-app'
        JENKINS_TOKEN = credentials('dagshub-token')
        GITHUB_CREDS = credentials('phish-token')
        PATH = "/var/jenkins_home/.local/bin:${env.PATH}"
    }

    triggers {
        pollSCM('* * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'phish-token', url: 'https://github.com/legit-os/phishing-detection.git']])
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                sh 'uv sync'
            }
        }

        stage('DVC Auth & Pull') {
            steps {
                sh 'uv run dvc remote modify origin --local auth basic'
                sh 'uv run dvc remote modify origin --local password ${JENKINS_TOKEN}'
                sh 'uv run dvc pull'
            }
        }
        
        stage('DVC Reproduce (Continuous Training)') {
            steps {
                sh 'uv run dvc repro'
            }
        }

        stage('Push Data & Models to DagsHub') {
            steps {
                sh 'uv run dvc push'
            }
        }

        stage('Commit & Push Lockfile to GitHub') {
            steps {
                sh 'git config user.email "jenkins@legit-os.com"'
                sh 'git config user.name "Jenkins CI"'
                sh 'git add dvc.lock'
                sh 'git commit -m "chore: auto-update dvc.lock after retraining [skip ci]" || true'
                sh 'git push https://${GITHUB_CREDS}@github.com/legit-os/phishing-detection.git HEAD:main || true'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:latest ."
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker-compose up -d --build --force-recreate app'
            }
        }
    }
}