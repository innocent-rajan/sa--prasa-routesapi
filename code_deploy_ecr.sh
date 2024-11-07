#!/bin/bash

# Check if tag argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <tag>"
  exit 1
fi

# Define variables
TAG=$1
AWS_REGION="ap-south-1"
ECR_REPO_ID="178761578367.dkr.ecr.ap-south-1.amazonaws.com"
IMAGE_NAME="rajkot-rrl-routesapi"
PROFILE_NAME="chartr"

# Log in to AWS ECR
aws ecr get-login-password --region ${AWS_REGION} --profile ${PROFILE_NAME} | docker login --username AWS --password-stdin ${ECR_REPO_ID}

# Build the Docker image
docker build -t ${IMAGE_NAME}:${TAG} .

# Tag the Docker image with the ECR repository URI
docker tag ${IMAGE_NAME}:${TAG} ${ECR_REPO_ID}/${IMAGE_NAME}:${TAG}

# Push the Docker image to the ECR repository
docker push ${ECR_REPO_ID}/${IMAGE_NAME}:${TAG}

echo "Docker image ${IMAGE_NAME}:${TAG} has been successfully built and pushed to ${ECR_REPO_ID}/${IMAGE_NAME}:${TAG}"
