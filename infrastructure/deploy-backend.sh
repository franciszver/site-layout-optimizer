#!/bin/bash

# Site Layout Optimizer - Backend Deployment Script
# Deploys FastAPI backend to AWS App Runner

set -e

ENVIRONMENT=${1:-dev}
REGION=${2:-us-east-1}
ECR_REPO_NAME="site-layout-optimizer-backend"
APP_RUNNER_SERVICE_NAME="site-layout-optimizer-backend-${ENVIRONMENT}"

echo "=========================================="
echo "Deploying Backend to AWS App Runner"
echo "Environment: ${ENVIRONMENT}"
echo "Region: ${REGION}"
echo "=========================================="

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install it first."
    exit 1
fi

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo ""
echo "Step 1: Creating ECR repository (if it doesn't exist)..."
aws ecr describe-repositories --repository-names ${ECR_REPO_NAME} --region ${REGION} 2>/dev/null || \
  aws ecr create-repository --repository-name ${ECR_REPO_NAME} --region ${REGION} --image-scanning-configuration scanOnPush=true

echo ""
echo "Step 2: Logging in to ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY_URI}

echo ""
echo "Step 3: Building Docker image..."
cd "$(dirname "$0")/.."
docker build -t ${ECR_REPO_NAME}:latest -f backend/Dockerfile .

echo ""
echo "Step 4: Tagging image for ECR..."
docker tag ${ECR_REPO_NAME}:latest ${ECR_REPOSITORY_URI}:latest

echo ""
echo "Step 5: Pushing image to ECR..."
docker push ${ECR_REPOSITORY_URI}:latest

echo ""
echo "Step 6: Deploying to App Runner..."
echo "Note: If the App Runner service doesn't exist, you'll need to create it manually in the AWS Console"
echo "or use the AWS CLI command below:"
echo ""
echo "aws apprunner create-service --cli-input-json file://infrastructure/apprunner-service.json --region ${REGION}"
echo ""
echo "For now, if the service exists, updating it..."

# Check if service exists
if aws apprunner describe-service --service-arn "arn:aws:apprunner:${REGION}:${AWS_ACCOUNT_ID}:service/${APP_RUNNER_SERVICE_NAME}" --region ${REGION} 2>/dev/null; then
    echo "Service exists. Updating..."
    aws apprunner start-deployment \
      --service-arn "arn:aws:apprunner:${REGION}:${AWS_ACCOUNT_ID}:service/${APP_RUNNER_SERVICE_NAME}" \
      --region ${REGION}
else
    echo ""
    echo "=========================================="
    echo "Service does not exist yet."
    echo "Please create it manually in AWS Console:"
    echo "1. Go to AWS App Runner Console"
    echo "2. Click 'Create service'"
    echo "3. Select 'Container registry' -> 'Amazon ECR'"
    echo "4. Select repository: ${ECR_REPO_NAME}"
    echo "5. Configure environment variables"
    echo "6. Deploy"
    echo ""
    echo "Or use the provided apprunner-service.json template"
    echo "=========================================="
fi

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "ECR Repository: ${ECR_REPOSITORY_URI}"
echo "=========================================="

