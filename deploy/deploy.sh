#!/bin/bash

# Deploy builds to Kubernetes!
#
# This script can be used to deploy builds to Kubernetes using Helm.
#
# Params:
# - chart name (not including repository name)
# - namespace (used to select other env vars, see below)
#
# Pre-requisites:
# - Must have already provisioned an SA for Tiller, and initialized the Tiller
#   service in the target namespace.
# - Must have already provisioned an SA for Travis in the target namespace.
#   The following env vars should be set, e.g. in the Travis-CI interface:
#   - USER_SA_{namespace} = the service account name
#   - USER_TOKEN_{namespace} = base64-encoded bearer token for the Travis SA.
# - In addition, the following env vars must be set to configure access to
#   the Kubernetes API server:
#   - CLUSTER_ENDPOINT = URI of the K8s API server
#   - CA_CERT = base64 encoded root CA of the K8s cluster
#   - CLUSTER_NAME = the name of the cluster
# - The following env vars must be set for Helm to work:
#   - HELM_REPOSITORY = the location of the arXiv helm repository,
#     e.g. s3://...
# - DEPLOYMENT_DOMAIN_{namespace}

CHART_NAME=$1
ENVIRONMENT=$2
TOKEN_NAME=USER_TOKEN_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
SA_NAME=USER_SA_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
DEPLOYMENT_HOSTNAME_VAR=DEPLOYMENT_DOMAIN_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
USER_TOKEN=${!TOKEN_NAME}
USER_SA=${!SA_NAME}
HELM_RELEASE=${CHART_NAME}-${ENVIRONMENT}
DEPLOYMENT_HOSTNAME=${!DEPLOYMENT_HOSTNAME_VAR}

REDIS_SECRET_NAME_VAR=REDIS_SECRET_NAME_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
REDIS_SECRET_NAME=${!REDIS_SECRET_NAME_VAR}
DATABASE_SECRET_NAME_VAR=DATABASE_SECRET_NAME_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
DATABASE_SECRET_NAME=${!DATABASE_SECRET_NAME_VAR}
DJANGO_SECRET_NAME_VAR=DJANGO_SECRET_NAME_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
DJANGO_SECRET_NAME=${!DJANGO_SECRET_NAME_VAR}
VAULT_SECRET_NAME_VAR=VAULT_SECRET_NAME_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
VAULT_SECRET_NAME=${!VAULT_SECRET_NAME_VAR}
S3_BUCKET_VAR=S3_BUCKET_$(echo $ENVIRONMENT | awk '{print toupper($0)}')
S3_BUCKET=${!S3_BUCKET_VAR}

if [ -z "$SITE_SEARCH_ENABLED" ]; then SITE_SEARCH_ENABLED="1"; fi

if [ -z "${TRAVIS_TAG}" ]; then
    IMAGE_TAG=${TRAVIS_COMMIT}
else
    IMAGE_TAG=${TRAVIS_TAG}
fi
IMAGE_NAME=arxiv/readability

# Build and push the docker image.
docker login -u "$DOCKERHUB_USERNAME" -p "$DOCKERHUB_PASSWORD"
docker build . -t ${IMAGE_NAME}:${IMAGE_TAG};
docker push ${IMAGE_NAME}:${IMAGE_TAG}

if [[ ! $TRAVIS_BRANCH =~ "^develop|master$" ]]; then
    SLUG_BRANCHNAME=$(echo $TRAVIS_BRANCH | iconv -t ascii//TRANSLIT | sed -E 's/[~\^]+//g' | sed -E 's/[^a-zA-Z0-9]+/-/g' | sed -E 's/^-+\|-+$//g' | sed -E 's/^-+//g' | sed -E 's/-+$//g' | tr A-Z a-z);
    HELM_RELEASE=$CHART_NAME"-"$SLUG_BRANCHNAME
    DEPLOYMENT_HOSTNAME=$CHART_NAME"-"$SLUG_BRANCHNAME"."$DEPLOYMENT_HOSTNAME
else
    DEPLOYMENT_HOSTNAME=$CHART_NAME"."$DEPLOYMENT_HOSTNAME
fi

echo "Deploying ${CHART_NAME} in ${ENVIRONMENT}"


# Deploy to Kubernetes.
helm get $HELM_RELEASE --tiller-namespace $ENVIRONMENT 2> /dev/null \
    && helm upgrade $HELM_RELEASE arxiv/$CHART_NAME \
        --set=image.tag=$TRAVIS_COMMIT \
        --set=deployment.name=$HELM_RELEASE \
        --set=service.name=$HELM_RELEASE \
        --set=database.secret.name=$DATABASE_SECRET_NAME \
        --set=database.secret.key=uri \
        --set=secrets.jwt.name=$JWT_SECRET_NAME \
        --set=secrets.jwt.key=$JWT_SECRET_KEY \
        --set=namespace=$ENVIRONMENT \
        --tiller-namespace $ENVIRONMENT \
        --namespace $ENVIRONMENT  \
    || helm install arxiv/$CHART_NAME \
        --name=$HELM_RELEASE \
        --set=image_tag=$TRAVIS_COMMIT \
        --set=deployment.name=$HELM_RELEASE \
        --set=service.name=$HELM_RELEASE \
        --set=database.secret.name=$DATABASE_SECRET_NAME \
        --set=database.secret.key=uri \
        --set=secrets.jwt.name=$JWT_SECRET_NAME \
        --set=secrets.jwt.key=$JWT_SECRET_KEY \
        --set=namespace=$ENVIRONMENT \
        --tiller-namespace $ENVIRONMENT \
        --namespace $ENVIRONMENT
DEPLOY_EXIT=$?

# Send the result back to GitHub.
if [ $DEPLOY_EXIT -ne 0 ]; then
    DEPLOY_STATE="failure"
    echo "Deployment failed"
else
    DEPLOY_STATE="success"
    echo "Deployed!"
fi

if [ "$TRAVIS_PULL_REQUEST_SHA" = "" ];  then SHA=$TRAVIS_COMMIT; else SHA=$TRAVIS_PULL_REQUEST_SHA; fi
curl -u $USERNAME:$GITHUB_TOKEN \
    -d '{"state": "'$DEPLOY_STATE'", "target_url": "https://'$DEPLOYMENT_HOSTNAME'", "description": "Deploy '$DEPLOY_STATE' for '$DEPLOYMENT_HOSTNAME'", "context": "deploy/readability"}' \
    -XPOST https://api.github.com/repos/$TRAVIS_REPO_SLUG/statuses/$SHA > /dev/null 2>&1 && \
    echo "Sent result to GitHub"

function cleanup {
    printf "Cleaning up...\n"
    rm -vf "${HOME}/ca.crt"
    printf "Cleaning done."
}

trap cleanup EXIT
