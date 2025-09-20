pipeline {
    agent any

    environment {
        AWS_DEFAULT_REGION = 'us-east-1'
        ECR_REGISTRY = "992382545251.dkr.ecr.us-east-1.amazonaws.com"
        ECR_REPOSITORY = 'status-page-aaj-ecr'
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('CI - Test & Build') {
            when {
                changeRequest() // Only on Pull Requests
            }
            steps {
                script {
                    echo "Running CI for Pull Request"
                    // Build image for testing
                    def testImage = docker.build("${ECR_REPOSITORY}:test-${BUILD_NUMBER}")
                    
                    // Run tests inside the container
                    testImage.inside {
                        sh '''
                            cd statuspage
                            python manage.py check --deploy
                            echo "All CI checks passed!"
                        '''
                    }
                }
            }
        }

        stage('CD - Build for Production') {
            when {
                branch 'main' // Only on main branch
            }
            steps {
                script {
                    echo "Running CD for main branch"
                    docker.build("${ECR_REPOSITORY}:${IMAGE_TAG}")
                }
            }
        }

        stage('CD - Push to ECR') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh '''
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                    '''
                }
            }
        }

        stage('CD - Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh '''
                        # Pull the latest image from ECR
                        docker pull ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest

                        # Stop and remove existing container if running
                        docker stop status-page-app || true
                        docker rm status-page-app || true

                        # Run new container
                        docker run -d \
                            --name status-page-app \
                            -p 8000:8000 \
                            ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                    '''
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    sh '''
                        # Remove local test/build images to save space
                        docker rmi ${ECR_REPOSITORY}:${IMAGE_TAG} || true
                        docker rmi ${ECR_REPOSITORY}:test-${BUILD_NUMBER} || true
                        docker rmi ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} || true
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}