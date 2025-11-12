#!/bin/bash

# Site Layout Optimizer - Deployment Script
# This script deploys the AWS infrastructure using AWS SAM

set -e

ENVIRONMENT=${1:-dev}
STACK_NAME="site-layout-optimizer-${ENVIRONMENT}"

echo "Deploying Site Layout Optimizer to ${ENVIRONMENT} environment..."

# Build and deploy using SAM
sam build --template-file infrastructure/template.yaml
sam deploy \
  --stack-name ${STACK_NAME} \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Environment=${ENVIRONMENT} \
    DatabaseUsername=${DATABASE_USERNAME:-postgres} \
    DatabasePassword=${DATABASE_PASSWORD} \
  --region us-east-1 \
  --confirm-changeset

echo "Deployment complete!"
echo "Stack outputs:"
aws cloudformation describe-stacks \
  --stack-name ${STACK_NAME} \
  --query 'Stacks[0].Outputs' \
  --output table

