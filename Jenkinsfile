pipeline {
    agent any

    options {
        skipDefaultCheckout()
    }

    environment {
        DOCKER_IMAGE = 'phishing-detection-app'
        JENKINS_TOKEN = credentials('dagshub-token')
        GITHUB_CREDS = credentials('phish-token')
        PATH = "/root/.local/bin:/var/jenkins_home/.local/bin:${env.PATH}"
    }

    triggers {
        pollSCM('* * * * *')
    }

    stages {
        stage('Clean Workspace') {
            steps {
                echo 'Purging corrupt temporary caches...'
                // Deletes Jenkins' local workspace to guarantee a completely fresh download
                cleanWs() 
            }
        }

        stage('Checkout') {
            steps {
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'phish-token', url: 'https://github.com/legit-os/phishing-detection.git']])
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'apt-get update && apt-get install -y libgomp1 docker.io docker-compose'
                sh 'curl -LsSf https://astral.sh/uv/install.sh | sh'
                sh 'uv sync'
            }
        }

        stage('DVC Auth & Pull') {
            steps {
                sh 'uv run dvc remote modify dagshub --local auth basic'
                sh 'uv run dvc remote modify dagshub --local user legit-os'
                sh 'uv run dvc remote modify dagshub --local password ${JENKINS_TOKEN}'
                sh 'uv run dvc pull'
            }
        }
        
        stage('DVC Reproduce & Approve') {
            steps {
                script {
                    def approved = false
                    def maxRetries = 3
                    def attempt = 0

                    while (!approved && attempt < maxRetries) {
                        attempt++
                        echo "=== Training Attempt ${attempt}/${maxRetries} ==="

                        sh 'uv run dvc repro'
                        sh 'uv run python pipeline/show_eval.py models/models_registry.json'

                        try {
                            input message: "Review the model metrics above. Do you approve these models for deployment?",
                                  ok: 'Approve',
                                  submitter: ''
                            approved = true
                            echo 'Models APPROVED — proceeding to deployment.'
                        } catch (err) {
                            echo "Models REJECTED (attempt ${attempt}/${maxRetries}). Re-running training..."
                            if (attempt >= maxRetries) {
                                error "Maximum retries (${maxRetries}) reached. Pipeline aborted."
                            }
                        }
                    }
                }
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
                sh 'docker-compose -p phishing-detection up -d --build --force-recreate app'
            }
        }
    }
}