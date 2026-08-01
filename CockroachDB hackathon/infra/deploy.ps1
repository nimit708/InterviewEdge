<#
.SYNOPSIS
    Deploy LedgerMind infrastructure and services to AWS.

.DESCRIPTION
    This script:
    1. Initializes Terraform and creates AWS infrastructure
    2. Builds Docker images for each service
    3. Pushes images to ECR
    4. Updates ECS services

.PARAMETER Action
    What to deploy: "infra", "services", "all"

.EXAMPLE
    .\deploy.ps1 -Action all
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("infra", "services", "all")]
    [string]$Action = "all"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$InfraDir = $PSScriptRoot

Write-Host "=== LedgerMind Deployment ===" -ForegroundColor Cyan
Write-Host "Action: $Action" -ForegroundColor Yellow

# --- Step 1: Infrastructure ---
if ($Action -eq "infra" -or $Action -eq "all") {
    Write-Host "`n--- Deploying Infrastructure ---" -ForegroundColor Green

    Set-Location $InfraDir

    # Initialize Terraform
    Write-Host "Initializing Terraform..."
    terraform init

    # Plan
    Write-Host "Planning infrastructure changes..."
    terraform plan -out=tfplan

    # Apply
    Write-Host "Applying infrastructure..."
    $confirm = Read-Host "Apply changes? (yes/no)"
    if ($confirm -eq "yes") {
        terraform apply tfplan
    } else {
        Write-Host "Skipping infrastructure apply." -ForegroundColor Yellow
    }

    # Capture outputs
    $AWS_REGION = terraform output -raw aws_region 2>$null
    if (-not $AWS_REGION) { $AWS_REGION = "us-east-1" }
    $ECR_API = terraform output -raw ecr_api_url
    $ECR_WEBHOOK = terraform output -raw ecr_webhook_url
    $ECR_WORKER = terraform output -raw ecr_worker_url
    $ECR_AGENT = terraform output -raw ecr_agent_url
    $ECS_CLUSTER = terraform output -raw ecs_cluster_name

    Set-Location $ProjectRoot
}

# --- Step 2: Build and Push Services ---
if ($Action -eq "services" -or $Action -eq "all") {
    Write-Host "`n--- Building and Pushing Services ---" -ForegroundColor Green

    # Get AWS account ID
    $AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
    if (-not $AWS_REGION) { $AWS_REGION = "us-east-1" }

    # Read ECR URLs from Terraform output if not already set
    if (-not $ECR_API) {
        Set-Location $InfraDir
        $ECR_API = terraform output -raw ecr_api_url
        $ECR_WEBHOOK = terraform output -raw ecr_webhook_url
        $ECR_WORKER = terraform output -raw ecr_worker_url
        $ECR_AGENT = terraform output -raw ecr_agent_url
        $ECS_CLUSTER = terraform output -raw ecs_cluster_name
        Set-Location $ProjectRoot
    }

    # Login to ECR
    Write-Host "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

    # Build and push API
    Write-Host "Building API image..."
    docker build -t "${ECR_API}:latest" -f backend/Dockerfile backend/
    docker push "${ECR_API}:latest"

    # Build and push Webhook (same Dockerfile, different CMD)
    Write-Host "Building Webhook image..."
    docker build -t "${ECR_WEBHOOK}:latest" -f backend/Dockerfile backend/
    docker push "${ECR_WEBHOOK}:latest"

    # Build and push Worker
    Write-Host "Building Worker image..."
    docker build -t "${ECR_WORKER}:latest" -f backend/Dockerfile backend/
    docker push "${ECR_WORKER}:latest"

    # Build and push Agent
    Write-Host "Building Agent image..."
    docker build -t "${ECR_AGENT}:latest" -f backend/Dockerfile backend/
    docker push "${ECR_AGENT}:latest"

    # Force new deployment on ECS
    Write-Host "Updating ECS services..."
    aws ecs update-service --cluster $ECS_CLUSTER --service "ledgermind-dev-api" --force-new-deployment --region $AWS_REGION
    aws ecs update-service --cluster $ECS_CLUSTER --service "ledgermind-dev-webhook" --force-new-deployment --region $AWS_REGION
    aws ecs update-service --cluster $ECS_CLUSTER --service "ledgermind-dev-worker" --force-new-deployment --region $AWS_REGION
    aws ecs update-service --cluster $ECS_CLUSTER --service "ledgermind-dev-agent" --force-new-deployment --region $AWS_REGION

    Write-Host "ECS services updated. Waiting for deployment..." -ForegroundColor Green
}

Write-Host "`n=== Deployment Complete ===" -ForegroundColor Cyan
Write-Host "Run 'terraform output' in infra/ to see all endpoints and configuration values."
