pipeline {
    agent {
        kubernetes {
            yaml """
            apiVersion: v1
            kind: Pod
            spec:
              containers:
              - name: jnlp
                image: orielias/my-custom-jenkins-agent:latest
                args: ['\$(JENKINS_SECRET)', '\$(JENKINS_NAME)']
                tty: true
              - name: docker
                image: docker:latest
                command:
                - cat
                tty: true
                volumeMounts:
                - mountPath: /var/run/docker.sock
                  name: docker-sock
              volumes:
              - name: docker-sock
                hostPath:
                  path: /var/run/docker.sock
            """
        }
    }
    options {
        buildDiscarder logRotator(artifactDaysToKeepStr: '', artifactNumToKeepStr: '5', daysToKeepStr: '', numToKeepStr: '5')
    }
    environment {
        DOCKERHUB_CREDENTIALS = credentials('docker-hub-credentials') // Docker Hub credentials
        IMAGE_TAG = "orielias/weather_app:${env.BUILD_ID}"  // Image tag
        KUBECONFIG_CREDENTIALS_ID = 'jenkins-kubernetes-token'  // The ID you used when you created the credentials
    }
    stages {
        stage('Build Docker Image') {
            steps {
                container('docker') {
                    script {
                        sh "docker build -t ${IMAGE_TAG} ."
                    }
                }
            }
        }
        stage('Push Image to DockerHub') {
            steps {
                container('docker') {
                    script {
                        sh 'echo "pushing to dockerhub..."'
                        withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                            sh 'docker login -u $DOCKERHUB_USERNAME -p $DOCKERHUB_PASSWORD'
                            sh "docker push ${IMAGE_TAG}"
                        }
                    }
                }
            }
        }
        stage('Update Deployment File') {
            steps {
                container('docker') {
                    script {
                        sh "sed -i 's|<IMAGE_TAG>|${IMAGE_TAG}|g' deployment.yml"
                    }
                }
            }
        }
        stage('Deploy Application') {
            steps {
                script {
                    withCredentials([string(credentialsId: KUBECONFIG_CREDENTIALS_ID, variable: 'KUBE_TOKEN')]) {
                        sh '''
                        echo -n "$KUBE_TOKEN" > /tmp/token.txt
                        kubectl config set-credentials jenkins --token="$(cat /tmp/token.txt)"
                        kubectl config set-cluster default-cluster --server=https://172.31.21.65:6443 --insecure-skip-tls-verify=true
                        kubectl config set-context default --cluster=default-cluster --user=jenkins
                        kubectl config use-context default
                        kubectl apply -f deployment.yml
                        '''
                    }
                }
            }
        }
    }
}
