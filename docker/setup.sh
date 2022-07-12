#!/usr/bin/env bash

# Change these values for your own environment
# it should match what values you use in the CDK app
# if you are using this script together to deploy
# the multi-arch demo

AWS_DEFAULT_REGION=eu-west-2
AWS_ACCOUNT=704533066374
AWS_ECR_REPO=hybrid-airflow
COMMIT_HASH="airflw"

# You can alter these values, but the defaults will work for any environment

IMAGE_TAG=${COMMIT_HASH:=latest}
AMD_TAG=${COMMIT_HASH}-amd64
DOCKER_CLI_EXPERIMENTAL=enabled
REPOSITORY_URI=$AWS_ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$AWS_ECR_REPO

# Login to ECR
# Old deprecated
# $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com

# create AWS ECR Repo

if (aws ecr describe-repositories --repository-names $AWS_ECR_REPO ) then
	echo "Skipping the create repo as already exists"
else
	echo "Creating repos as it does not exists"
	aws ecr create-repository --region $AWS_DEFAULT_REGION --repository-name $AWS_ECR_REPO
fi

# Build initial image and upload to ECR Repo

docker build -t $REPOSITORY_URI:latest .
docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$AMD_TAG
docker push $REPOSITORY_URI:$AMD_TAG

# Create the image manifests and upload to ECR

docker manifest create $REPOSITORY_URI:$COMMIT_HASH $REPOSITORY_URI:$AMD_TAG
docker manifest annotate --arch amd64 $REPOSITORY_URI:$COMMIT_HASH $REPOSITORY_URI:$AMD_TAG
docker manifest inspect $REPOSITORY_URI:$COMMIT_HASH
docker manifest push $REPOSITORY_URI:$COMMIT_HASH
