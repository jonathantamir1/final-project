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

        // CI: Build and test image (runs on ALL branches including PRs)
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image for testing/deployment"
                    docker.build("${ECR_REPOSITORY}:${IMAGE_TAG}")
                }
            }
        }

        // CI: Run tests (runs on ALL branches including PRs)
        stage('Run Tests') {
            steps {
                script {
                    echo "Running tests and checks"
                    sh '''
                        # Test the built image
                        docker run --rm ${ECR_REPOSITORY}:${IMAGE_TAG} sh -c "cd statuspage && python manage.py check"
                        echo "All tests passed!"
                    '''
                }
            }
        }

        // CD: Push to ECR (ONLY on main branch)
        stage('Push to ECR') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "Pushing to ECR - main branch deployment"
                    sh '''
                        # Login to ECR
                        aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                        
                        # Tag images
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        
                        # Push to ECR
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                        docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                    '''
                }
            }
        }

        // CD: Deploy (ONLY on main branch)
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "Deploying to production"
                    sh '''
                        # Stop existing container
                        docker stop status-page-app || true
                        docker rm status-page-app || true

                        # Run new container from ECR
                        docker run -d \
                            --name status-page-app \
                            -p 8000:8000 \
                            --restart unless-stopped \
                            ${ECR_REGISTRY}/${ECR_REPOSITORY}:latest
                        
                        # Verify deployment
                        sleep 10
                        docker ps | grep status-page-app
                        echo "Deployment completed successfully!"
                    '''
                }
            }
        }

        // Always cleanup local images
        stage('Cleanup') {
            steps {
                script {
                    sh '''
                        # Remove local images to save disk space
                        docker rmi ${ECR_REPOSITORY}:${IMAGE_TAG} || true
                        docker system prune -f
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                // Always cleanup workspace and Docker
                sh 'docker system prune -f || true'
                cleanWs()
            }
        }
        success {
            script {
                if (env.BRANCH_NAME == 'main') {
                    echo 'CD Pipeline succeeded! Application deployed to production.'
                } else {
                    echo 'CI Pipeline succeeded! Code is ready for merge.'
                }
            }
        }
        failure {
            script {
                if (env.BRANCH_NAME == 'main') {
                    echo 'CD Pipeline failed! Production deployment unsuccessful.'
                } else {
                    echo 'CI Pipeline failed! Please fix issues before merging.'
                }
            }
        }
    }
}