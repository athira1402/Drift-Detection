pipeline {
    agent any
    environment {
        // Automatically detects the Host IP for the API calls
        HOST_IP = sh(script: "hostname -I | awk '{print \$1}'", returnStdout: true).trim()
        KUBECONFIG = credentials('kubeconfig') 
    }
    stages {
        stage('Environment Setup') {
            steps {
                withCredentials([string(credentialsId: 'ansible-vault-pass', variable: 'VAULT_PW')]) {
                    sh 'echo $VAULT_PW > .vault_pass'
                    sh 'ansible-playbook -i ansible/inventory.ini ansible/site.yml --vault-password-file .vault_pass'
                    sh 'rm .vault_pass'
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    python3 -m unittest data_ingestion/tests/test_ingestion.py
                    python3 -m unittest drift_detection/tests/test_drift_detection.py
                    python3 -m unittest model_serving/tests/test_serving.py
                    python3 -m unittest model_training/tests/test_training.py
                '''
            }
        }

        stage('Integration Testing') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                script {
                    sh 'docker compose -f docker-compose.test.yml down --remove-orphans'
                    sh 'docker compose -f docker-compose.test.yml up --build -d'
                    
                    echo "Waiting for Flask services to initialize..."
                    sleep 15

                    // Bootstrap Training
                    echo "Training baseline model..."
                    def trainStatus = sh(script: """
                        curl -s -X POST http://${HOST_IP}:5001/train \
                        -H "Content-Type: application/json" \
                        -d '[{"CustomerId": 1, "CreditScore": 600, "Geography": "France", "Gender": "Male", "Age": 30, "Tenure": 5, "Balance": 1000.0, "NumOfProducts": 1, "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 40000.0, "Exited": 0}]'
                    """, returnStdout: true).trim()
                    
                    if (!trainStatus.contains("success")) {
                        error "Model Training failed: ${trainStatus}"
                    }
                    sleep 10
                }
            }
            post {
                always {
                    sh 'docker compose -f docker-compose.test.yml down || true'
                }
            }
        }

        stage('Build & Push Images') {
            parallel {
                stage('Ingestion') {
                    steps {
                        dir('data_ingestion') {
                            withCredentials([usernamePassword(credentialsId: 'DockerHubCred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {  
                                sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                                sh 'docker build -t athira1402/data_ingestion:latest -f Dockerfile.ingest .'
                                sh 'docker push athira1402/data_ingestion:latest'
                            }
                        }
                    }
                }
                stage('Training') {
                    steps {
                        dir('model_training') {
                            withCredentials([usernamePassword(credentialsId: 'DockerHubCred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {  
                                sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                                sh 'docker build -t athira1402/model_training:latest -f Dockerfile.training .'
                                sh 'docker push athira1402/model_training:latest'
                            }
                        }
                    }
                }
                stage('Serving') {
                    steps {
                        dir('model_serving') {
                            withCredentials([usernamePassword(credentialsId: 'DockerHubCred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                                sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                                sh 'docker build -t athira1402/model_serving:latest -f Dockerfile.serving .'
                                sh 'docker push athira1402/model_serving:latest'
                            }
                        }
                    }
                }
                stage('Drift') {
                    steps {
                        dir('drift_detection') {
                            withCredentials([usernamePassword(credentialsId: 'DockerHubCred', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                                sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"             
                                sh 'docker build -t athira1402/drift_detection:latest -f Dockerfile.drift .'
                                sh 'docker push athira1402/drift_detection:latest'
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    export MINIKUBE_HOME=/home/athira
                    export KUBECONFIG=/home/athira/.kube/config
                    
                    echo "Applying Kubernetes manifests..."
                    kubectl apply -f kubernetes/pv.yaml --validate=false
                    kubectl apply -f kubernetes/pvc.yaml --validate=false
                    kubectl apply -f kubernetes/deployment/ --validate=false
                    kubectl apply -f kubernetes/service/ --validate=false
                    kubectl apply -f kubernetes/elk/ --validate=false
                    kubectl apply -f kubernetes/hpa.yaml --validate=false
                    
                    # Automate data sync to the training pod
                    echo "Waiting for training pod to be ready..."
                    kubectl wait --for=condition=Ready pod -l app=model-training --timeout=60s
                    TRAIN_POD=$(kubectl get pods -l app=model-training -o jsonpath='{.items[0].metadata.name}')
                    kubectl cp data/churn-model/train.csv ${TRAIN_POD}:/data/churn-model/train.csv
                '''
            }
        }

        stage('Automate Kibana Setup') {
            steps {
                script {
                    // Use the specific NodePort 30561 identified from your service list
                    def kibanaUrl = "http://${HOST_IP}:30561"
                    
                    sh """
                        echo "Waiting for Kibana to be reachable at ${kibanaUrl}..."
                        
                        # Wait loop: checks if Kibana status API returns 200 OK
                        until \$(curl -s -o /dev/null -w "%{http_code}" ${kibanaUrl}/api/status) -eq 200; do
                            echo "Kibana is starting up... sleeping 15s"
                            sleep 15
                        done

                        echo "✅ Kibana is UP. Creating project-logs-* index pattern..."
                        
                        curl -X POST "${kibanaUrl}/api/saved_objects/index-pattern/project-logs-pattern" \
                        -H "kbn-xsrf: true" \
                        -H "Content-Type: application/json" \
                        -d '{
                          "attributes": {
                            "title": "project-logs-*",
                            "timeFieldName": "@timestamp"
                          }
                        }' || echo "Notice: Index pattern setup skipped (possibly already exists)."
                    """
                }
            }
        }
    }
}