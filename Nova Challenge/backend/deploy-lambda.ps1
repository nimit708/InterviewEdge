# PowerShell script to deploy Lambda function using AWS CLI

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying InterviewEdge Backend Lambda..." -ForegroundColor Cyan

# Configuration
$FUNCTION_NAME = "InterviewEdge-API"
$REGION = "eu-west-2"
$RUNTIME = "python3.11"
$HANDLER = "main.handler"
$ROLE_NAME = "InterviewEdge-Lambda-Role"

# Check AWS credentials
Write-Host "`n✅ Checking AWS credentials..." -ForegroundColor Cyan
try {
    $identity = aws sts get-caller-identity | ConvertFrom-Json
    Write-Host "Authenticated as: $($identity.Arn)" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured. Run: aws configure" -ForegroundColor Red
    exit 1
}

# Create IAM role if it doesn't exist
Write-Host "`n📋 Creating IAM role..." -ForegroundColor Cyan
$trustPolicy = @"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
"@

$trustPolicy | Out-File -FilePath "trust-policy.json" -Encoding utf8

try {
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json --region $REGION 2>$null
    Write-Host "✅ IAM role created" -ForegroundColor Green
    Start-Sleep -Seconds 10
} catch {
    Write-Host "⚠️  Role already exists or creation failed, continuing..." -ForegroundColor Yellow
}

# Attach policies to role
Write-Host "`n📎 Attaching policies to role..." -ForegroundColor Cyan
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" --region $REGION
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AmazonBedrockFullAccess" --region $REGION
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AmazonPollyFullAccess" --region $REGION
aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn "arn:aws:iam::aws:policy/AmazonTranscribeFullAccess" --region $REGION

Write-Host "✅ Policies attached" -ForegroundColor Green

# Get role ARN
$ROLE_ARN = aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text --region $REGION
Write-Host "Role ARN: $ROLE_ARN" -ForegroundColor Cyan

# Package the Lambda function
Write-Host "`n📦 Packaging Lambda function..." -ForegroundColor Cyan
if (Test-Path "package") {
    Remove-Item -Recurse -Force package
}
New-Item -ItemType Directory -Path package | Out-Null

# Install dependencies
pip install -r requirements.txt -t package/ --quiet

# Copy main.py to package
Copy-Item main.py package/

# Create zip file
if (Test-Path "function.zip") {
    Remove-Item function.zip
}

Compress-Archive -Path package/* -DestinationPath function.zip

Write-Host "✅ Package created: function.zip" -ForegroundColor Green

# Wait for role to be ready
Write-Host "`n⏳ Waiting for IAM role to propagate..." -ForegroundColor Cyan
Start-Sleep -Seconds 15

# Create or update Lambda function
Write-Host "`n🚀 Deploying Lambda function..." -ForegroundColor Cyan
try {
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime $RUNTIME `
        --role $ROLE_ARN `
        --handler $HANDLER `
        --zip-file fileb://function.zip `
        --timeout 30 `
        --memory-size 512 `
        --region $REGION `
        --environment "Variables={AWS_REGION=$REGION}" 2>$null
    
    Write-Host "✅ Lambda function created" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Function exists, updating code..." -ForegroundColor Yellow
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://function.zip `
        --region $REGION
    
    Write-Host "✅ Lambda function updated" -ForegroundColor Green
}

# Create API Gateway
Write-Host "`n🌐 Creating API Gateway..." -ForegroundColor Cyan

# Create REST API
$apiResult = aws apigatewayv2 create-api `
    --name "InterviewEdge-API" `
    --protocol-type HTTP `
    --cors-configuration "AllowOrigins=*,AllowMethods=*,AllowHeaders=*" `
    --region $REGION | ConvertFrom-Json

$API_ID = $apiResult.ApiId
$API_ENDPOINT = $apiResult.ApiEndpoint

Write-Host "✅ API Gateway created: $API_ID" -ForegroundColor Green

# Create integration
$integrationResult = aws apigatewayv2 create-integration `
    --api-id $API_ID `
    --integration-type AWS_PROXY `
    --integration-uri "arn:aws:lambda:${REGION}:$($identity.Account):function:${FUNCTION_NAME}" `
    --payload-format-version "2.0" `
    --region $REGION | ConvertFrom-Json

$INTEGRATION_ID = $integrationResult.IntegrationId

# Create route
aws apigatewayv2 create-route `
    --api-id $API_ID `
    --route-key '$default' `
    --target "integrations/$INTEGRATION_ID" `
    --region $REGION | Out-Null

# Create stage
aws apigatewayv2 create-stage `
    --api-id $API_ID `
    --stage-name '$default' `
    --auto-deploy `
    --region $REGION | Out-Null

# Add Lambda permission for API Gateway
aws lambda add-permission `
    --function-name $FUNCTION_NAME `
    --statement-id apigateway-invoke `
    --action lambda:InvokeFunction `
    --principal apigateway.amazonaws.com `
    --source-arn "arn:aws:execute-api:${REGION}:$($identity.Account):${API_ID}/*" `
    --region $REGION 2>$null

Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "`n📋 API Gateway URL:" -ForegroundColor Cyan
Write-Host $API_ENDPOINT -ForegroundColor Yellow
Write-Host "`nUse this URL in your frontend REACT_APP_API_URL environment variable" -ForegroundColor Cyan

# Save URL to file
$API_ENDPOINT | Out-File -FilePath "api-url.txt" -Encoding utf8
Write-Host "`n💾 API URL saved to: api-url.txt" -ForegroundColor Green

# Cleanup
Remove-Item trust-policy.json -ErrorAction SilentlyContinue
