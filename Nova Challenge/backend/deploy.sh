#!/bin/bash

echo "🚀 Deploying InterviewEdge Backend to AWS..."

# Check if AWS SAM CLI is installed
if ! command -v sam &> /dev/null
then
    echo "❌ AWS SAM CLI is not installed."
    echo "Install it from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null
then
    echo "❌ AWS credentials not configured."
    echo "Run: aws configure"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Build the SAM application
echo "📦 Building SAM application..."
sam build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# Deploy the SAM application
echo "🚀 Deploying to AWS..."
sam deploy --guided

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📋 Getting API Gateway URL..."
    sam list stack-outputs --stack-name interviewedge-backend
else
    echo "❌ Deployment failed"
    exit 1
fi
