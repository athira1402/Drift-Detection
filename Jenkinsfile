pipeline {
    agent any
    environment {
        KUBECONFIG = credentials('kubeconfig')  // Jenkins secret file with kubeconfig
    }
    stages {
        stage('Deploy to Kind') {
            steps {
                sh '''
                echo "Using kubeconfig at $KUBECONFIG"
                kubectl config view --minify
                kubectl get nodes
                kubectl apply -f kubernetes/deployment/data_ingestion_deployment.yaml --validate=false
                '''
            }
        }
        stage('Build Data Ingestion') {
            steps {
                dir('data_ingestion') {
                    sh 'docker build -t kirtinigam003/data_ingestion:latest .'
                }
            }
        }
        stage('Build Model Training') {
            steps {
                dir('model_training') {
                    sh 'docker build -t kirtinigam003/model_training:latest .'
                }
            }
        }
        stage('Push Images') {
            steps {
                sh 'docker push kirtinigam003/data_ingestion:latest'
                sh 'docker push kirtinigam003/model_training:latest'
            }
        }
        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        kubectl config view
                        kubectl apply -f kubernetes/pv.yaml
                        kubectl apply -f kubernetes/pvc.yaml
                        kubectl apply -f kubernetes/deployement/data_ingestion_deployment.yaml
                        kubectl apply -f kubernetes/deployement/model_training_deployment.yaml
                        kubectl apply -f kubernetes/deployement/drift_detection_deployment.yaml
                        kubectl apply -f kubernetes/deployement/model_serving_deployment.yaml
                        kubectl apply -f kubernetes/service/model_serving_service.yaml
                        kubectl apply -f kubernetes/service/data_ingestion_service.yaml
                        kubectl apply -f kubernetes/service/model_training_service.yaml
                        kubectl apply -f kubernetes/service/drift_detection_service.yaml
                    '''
                }
            }
        }
    }
}
