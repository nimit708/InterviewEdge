# PowerShell deployment script for Windows

Write-Host "🚀 Deploying InterviewEdge Backend to AWS..." -ForegroundColor Cyan

# Check if AWS SAM CLI is installed
try {
    sam --version | Out-Null
    Write-Host "✅ AWS SAM CLI found" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS SAM CLI is not installed." -ForegroundColor Red
    Write-Host "Install it from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
}

# Check if AWS credentials are configured
try {
    aws sts get-caller-identity | Out-Null
    Write-Host "✅ AWS credentials configured" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS credentials not configured." -ForegroundColor Red
    Write-Host "Run: aws configure"
    exit 1
}

# Build the SAM application
Write-Host "`n📦 Building SAM application..." -ForegroundColor Cyan
sam build

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}

# Deploy the SAM application
Write-Host "`n🚀 Deploying to AWS..." -ForegroundColor Cyan
sam deploy --guided

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Deployment successful!" -ForegroundColor Green
    Write-Host "`n📋 Getting API Gateway URL..." -ForegroundColor Cyan
    sam list stack-outputs --stack-name interviewedge-backend
} else {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}
