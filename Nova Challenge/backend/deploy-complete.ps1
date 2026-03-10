# Complete deployment script for InterviewEdge Backend
$ErrorActionPreference = "Stop"

Write-Host "Starting InterviewEdge Backend Deployment..." -ForegroundColor Cyan

$REGION = "eu-west-2"
$STACK_NAME = "InterviewEdge-Backend"
$FUNCTION_NAME = "InterviewEdge-API"
$LAYER_NAME = "interview-edge-dependencies"

# Step 1: Deploy CloudFormation Stack
Write-Host "`nStep 1: Deploying CloudFormation Stack..." -ForegroundColor Cyan
aws cloudformation deploy `
    --template-file cloudformation-template.yaml `
    --stack-name $STACK_NAME `
    --region $REGION `
    --capabilities CAPABILITY_IAM

if ($LASTEXITCODE -ne 0) {
    Write-Host "CloudFormation deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "CloudFormation stack deployed successfully" -ForegroundColor Green

# Get stack outputs
$outputs = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --region $REGION `
    --query 'Stacks[0].Outputs' | ConvertFrom-Json

$API_URL = ($outputs | Where-Object { $_.OutputKey -eq "ApiUrl" }).OutputValue
$FUNCTION_ARN = ($outputs | Where-Object { $_.OutputKey -eq "FunctionArn" }).OutputValue

Write-Host "API URL: $API_URL" -ForegroundColor Yellow
Write-Host "Function ARN: $FUNCTION_ARN" -ForegroundColor Yellow

# Step 2: Publish Lambda Layer
Write-Host "`nStep 2: Publishing Lambda Layer..." -ForegroundColor Cyan

if (-not (Test-Path "layer.zip")) {
    Write-Host "layer.zip not found. Creating it now..." -ForegroundColor Yellow
    
    # Create layer structure
    if (Test-Path "python") {
        Remove-Item -Recurse -Force python
    }
    New-Item -ItemType Directory -Path python | Out-Null
    
    # Install dependencies
    pip install -r requirements.txt -t python/ --quiet
    
    # Create layer zip
    Compress-Archive -Path python -DestinationPath layer.zip -Force
    Remove-Item -Recurse -Force python
    
    Write-Host "layer.zip created" -ForegroundColor Green
}

$layerResult = aws lambda publish-layer-version `
    --layer-name $LAYER_NAME `
    --description "Dependencies for InterviewEdge" `
    --zip-file fileb://layer.zip `
    --compatible-runtimes python3.11 `
    --region $REGION | ConvertFrom-Json

$LAYER_ARN = $layerResult.LayerVersionArn
Write-Host "Layer published: $LAYER_ARN" -ForegroundColor Green

# Step 3: Package and Deploy Lambda Code
Write-Host "`nStep 3: Packaging Lambda Function Code..." -ForegroundColor Cyan

# Create deployment package (just main.py, dependencies are in layer)
if (Test-Path "function.zip") {
    Remove-Item function.zip
}

Compress-Archive -Path main.py -DestinationPath function.zip

Write-Host "function.zip created" -ForegroundColor Green

# Step 4: Update Lambda Function
Write-Host "`nStep 4: Updating Lambda Function..." -ForegroundColor Cyan

# Update function code
aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --zip-file fileb://function.zip `
    --region $REGION | Out-Null

Write-Host "Lambda code updated" -ForegroundColor Green

# Wait for update to complete
Write-Host "Waiting for function update to complete..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Update function configuration to add layer
aws lambda update-function-configuration `
    --function-name $FUNCTION_NAME `
    --layers $LAYER_ARN `
    --region $REGION | Out-Null

Write-Host "Lambda layer attached" -ForegroundColor Green

# Step 5: Test the deployment
Write-Host "`nStep 5: Testing the deployment..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

try {
    $response = Invoke-RestMethod -Uri "$API_URL/health" -Method Get -ErrorAction SilentlyContinue
    Write-Host "API is responding" -ForegroundColor Green
} catch {
    Write-Host "API test failed, but deployment completed. The function may need a moment to initialize." -ForegroundColor Yellow
}

# Step 6: Save deployment info
Write-Host "`nStep 6: Saving deployment information..." -ForegroundColor Cyan

$deploymentInfo = @{
    ApiUrl = $API_URL
    FunctionName = $FUNCTION_NAME
    FunctionArn = $FUNCTION_ARN
    LayerArn = $LAYER_ARN
    Region = $REGION
    DeploymentTime = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

$deploymentInfo | ConvertTo-Json | Out-File -FilePath "deployment-info.json" -Encoding utf8
$API_URL | Out-File -FilePath "api-url.txt" -Encoding utf8

Write-Host "`nDeployment Complete!" -ForegroundColor Green
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "`nAPI Gateway URL:" -ForegroundColor White
Write-Host "  $API_URL" -ForegroundColor Yellow
Write-Host "`nLambda Function:" -ForegroundColor White
Write-Host "  Name: $FUNCTION_NAME" -ForegroundColor Yellow
Write-Host "  ARN: $FUNCTION_ARN" -ForegroundColor Yellow
Write-Host "`nLambda Layer:" -ForegroundColor White
Write-Host "  ARN: $LAYER_ARN" -ForegroundColor Yellow
Write-Host "`nRegion:" -ForegroundColor White
Write-Host "  $REGION" -ForegroundColor Yellow
Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "`nFor Amplify Configuration:" -ForegroundColor Cyan
Write-Host "  Add this to your frontend environment variables:" -ForegroundColor White
Write-Host "  REACT_APP_API_URL=$API_URL" -ForegroundColor Yellow
Write-Host "`nDeployment info saved to: deployment-info.json" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
