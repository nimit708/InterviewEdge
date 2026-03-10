# Simple deployment script using Lambda layers
$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying InterviewEdge Backend..." -ForegroundColor Cyan

$FUNCTION_NAME = "InterviewEdge-API"
$LAYER_NAME = "InterviewEdge-Dependencies"
$REGION = "eu-west-2"

# Step 1: Create dependencies layer
Write-Host "`n📦 Creating Lambda layer with dependencies..." -ForegroundColor Cyan

# Clean up
if (Test-Path "python") { Remove-Item -Recurse -Force python }
if (Test-Path "layer.zip") { Remove-Item layer.zip }

# Install dependencies for layer
New-Item -ItemType Directory -Path "python" -Force | Out-Null
pip install -r requirements.txt -t python/ --quiet

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Create layer zip
Compress-Archive -Path python -DestinationPath layer.zip -Force
Write-Host "✅ Layer package created" -ForegroundColor Green

# Publish layer
Write-Host "`n📤 Publishing Lambda layer..." -ForegroundColor Cyan
$layerResult = aws lambda publish-layer-version `
    --layer-name $LAYER_NAME `
    --zip-file fileb://layer.zip `
    --compatible-runtimes python3.11 `
    --region $REGION | ConvertFrom-Json

$LAYER_ARN = $layerResult.LayerVersionArn
Write-Host "✅ Layer published: $LAYER_ARN" -ForegroundColor Green

# Step 2: Create function code zip (just main.py)
Write-Host "`n📦 Packaging function code..." -ForegroundColor Cyan

if (Test-Path "function.zip") { Remove-Item function.zip }
Compress-Archive -Path main.py -DestinationPath function.zip -Force

Write-Host "✅ Function code packaged" -ForegroundColor Green

# Step 3: Create or update Lambda function
Write-Host "`n🚀 Deploying Lambda function..." -ForegroundColor Cyan

try {
    # Try to create function
    $functionResult = aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime python3.11 `
        --role "arn:aws:iam::923906573163:role/InterviewEdge-Lambda-Role" `
        --handler main.handler `
        --zip-file fileb://function.zip `
        --timeout 30 `
        --memory-size 512 `
        --layers $LAYER_ARN `
        --region $REGION 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Lambda function created" -ForegroundColor Green
    } else {
        throw "Function creation failed"
    }
} catch {
    Write-Host "⚠️  Function exists, updating..." -ForegroundColor Yellow
    
    # Update function code
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://function.zip `
        --region $REGION | Out-Null
    
    # Update function configuration with new layer
    aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --layers $LAYER_ARN `
        --region $REGION | Out-Null
    
    Write-Host "✅ Lambda function updated" -ForegroundColor Green
}

# Step 4: Create API Gateway
Write-Host "`n🌐 Setting up API Gateway..." -ForegroundColor Cyan

# Check if API exists
$existingApis = aws apigatewayv2 get-apis --region $REGION | ConvertFrom-Json
$existingApi = $existingApis.Items | Where-Object { $_.Name -eq "InterviewEdge-API" }

if ($existingApi) {
    $API_ID = $existingApi.ApiId
    $API_ENDPOINT = $existingApi.ApiEndpoint
    Write-Host "⚠️  API Gateway already exists: $API_ID" -ForegroundColor Yellow
} else {
    # Create new API
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
        --integration-uri "arn:aws:lambda:${REGION}:923906573163:function:${FUNCTION_NAME}" `
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

    # Add Lambda permission
    aws lambda add-permission `
        --function-name $FUNCTION_NAME `
        --statement-id apigateway-invoke `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:923906573163:${API_ID}/*" `
        --region $REGION 2>$null

    Write-Host "✅ API Gateway configured" -ForegroundColor Green
}

# Step 5: Display results
Write-Host "`n✅ Deployment Complete!" -ForegroundColor Green
Write-Host "`n📋 API Gateway URL:" -ForegroundColor Cyan
Write-Host $API_ENDPOINT -ForegroundColor Yellow
Write-Host "`nUse this URL in your frontend REACT_APP_API_URL" -ForegroundColor Cyan

# Save to file
$API_ENDPOINT | Out-File -FilePath "api-url.txt" -Encoding utf8
Write-Host "`n💾 API URL saved to: api-url.txt" -ForegroundColor Green

# Test the API
Write-Host "`n🧪 Testing API..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$API_ENDPOINT/" -Method Get
    Write-Host "✅ API is responding: $($response | ConvertTo-Json -Compress)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  API test failed (may need a moment to warm up)" -ForegroundColor Yellow
}

# Cleanup
Write-Host "`n🧹 Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item -Recurse -Force python -ErrorAction SilentlyContinue
Remove-Item layer.zip -ErrorAction SilentlyContinue
Remove-Item function.zip -ErrorAction SilentlyContinue

Write-Host "✅ Done!" -ForegroundColor Green
