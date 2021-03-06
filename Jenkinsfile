node {
    // Mark the code checkout 'stage'....
    stage 'Checkout'

    // Get source code from GitHub
    git credentialsId: url: 'https://github.com/mlf4aiur/portal.git'

    // Mark the code build 'stage'....
    stage 'Bake Docker image'
    // Run the docker build
    def v = version('portal.py')
    def docker_tag = "${v}-${env.BUILD_NUMBER}"
    def dockerRepoName = 'kevin/portal'
    def image = docker.build(dockerRepoName, '.')

    // Push Docker image to private Docker registry
    stage 'Private Docker Registry'
    // Docker registry server defined in Jenkins global properties
    docker.withRegistry("${env.DKR_SERVER}", cred_dkr) {
        image.push()
        image.push("${docker_tag}")
    }

    stage 'Deploy to Dev Env'

    // Deploy this service to Development environment
    withCredentials([[$class: 'UsernamePasswordMultiBinding',
                      credentialsId: cred_aws,
                      usernameVariable: 'AWS_ACCESS_KEY_ID',
                      passwordVariable: 'AWS_SECRET_ACCESS_KEY']]) {
        withEnv(["AWS_DEFAULT_REGION=${region}",
                 "CLUSTER_NAME=${cluster_name}",
                 "SERVICE_NAME=${service_name}",
                 "REPO_NAME=${dockerRepoName}",
                 "TAG=${docker_tag}"]) {
            sh '''
                set +x
                echo AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION}
                echo CLUSTER_NAME: ${CLUSTER_NAME}
                echo SERVICE_NAME: ${SERVICE_NAME}

                docker run \\
                --rm \\
                -e "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}" \\
                -e "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}" \\
                -e "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}" \\
                silintl/ecs-deploy \\
                -c ${CLUSTER_NAME} \\
                -n ${SERVICE_NAME} \\
                -i ${env.DKR_SERVER}/${REPO_NAME}:${TAG} \\
                -m 50 \\
                -M 100 \\
                -t 240
            '''
        }
    }
}

stage name: 'Staging', concurrency: 1
node {
    deploy 'staging'
}

input message: "Does staging look good?"
try {
    checkpoint('Before production')
} catch (NoSuchMethodError _) {
    echo 'Checkpoint feature available in CloudBees Jenkins Enterprise.'
}

stage name: 'Production', concurrency: 1
node {
    input message: 'Deploy it to Production environment?', submitter: 'admin'
    echo 'Production server looks to be alive'
    deploy 'production'
    echo "Deployed to production"
}

def version(versionFile) {
    def matcher = readFile(versionFile) =~ '__version__ = \'(.+)\''
    matcher ? matcher[0][1] : '0.0.1'
}

def deploy(id) {
    sh "echo ${id}"
}
