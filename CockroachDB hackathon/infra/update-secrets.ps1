<#
.SYNOPSIS
    Update AWS Secrets Manager with actual credentials.

.DESCRIPTION
    Run this after:
    1. CockroachDB Cloud cluster is created
    2. Stripe account is set up in test mode
    3. Terraform has been applied (creates the secret placeholders)

.EXAMPLE
    .\update-secrets.ps1
#>

$ErrorActionPreference = "Stop"

$AWS_REGION = "us-east-1"
$PROJECT = "ledgermind"
$ENV = "dev"

Write-Host "=== Update LedgerMind Secrets ===" -ForegroundColor Cyan
Write-Host "This will update secrets in AWS Secrets Manager." -ForegroundColor Yellow
Write-Host ""

# --- CockroachDB ---
Write-Host "--- CockroachDB Cloud ---" -ForegroundColor Green
$crdb_host = Read-Host "CockroachDB host (e.g., your-cluster.cockroachlabs.cloud)"
$crdb_user = Read-Host "CockroachDB username"
$crdb_pass = Read-Host "CockroachDB password" -AsSecureString
$crdb_pass_plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($crdb_pass))
$crdb_database = Read-Host "Database name (default: ledgermind)"
if (-not $crdb_database) { $crdb_database = "ledgermind" }

$crdb_url = "postgresql://${crdb_user}:${crdb_pass_plain}@${crdb_host}:26257/${crdb_database}?sslmode=verify-full"

$crdb_secret = @{
    url      = $crdb_url
    host     = $crdb_host
    port     = 26257
    database = $crdb_database
    username = $crdb_user
    password = $crdb_pass_plain
} | ConvertTo-Json

aws secretsmanager put-secret-value `
    --secret-id "$PROJECT/$ENV/cockroachdb-url" `
    --secret-string $crdb_secret `
    --region $AWS_REGION

Write-Host "CockroachDB secret updated." -ForegroundColor Green

# --- Stripe ---
Write-Host "`n--- Stripe (Test Mode) ---" -ForegroundColor Green
$stripe_sk = Read-Host "Stripe Secret Key (sk_test_...)"
$stripe_pk = Read-Host "Stripe Publishable Key (pk_test_...)"
$stripe_wh = Read-Host "Stripe Webhook Secret (whsec_...)"

$stripe_secret = @{
    secret_key      = $stripe_sk
    publishable_key = $stripe_pk
    webhook_secret  = $stripe_wh
} | ConvertTo-Json

aws secretsmanager put-secret-value `
    --secret-id "$PROJECT/$ENV/stripe" `
    --secret-string $stripe_secret `
    --region $AWS_REGION

Write-Host "Stripe secret updated." -ForegroundColor Green

# --- Summary ---
Write-Host "`n=== Secrets Updated ===" -ForegroundColor Cyan
Write-Host "CockroachDB: $PROJECT/$ENV/cockroachdb-url"
Write-Host "Stripe:      $PROJECT/$ENV/stripe"
Write-Host "Bedrock:     $PROJECT/$ENV/bedrock (already set by Terraform)"
Write-Host "App:         $PROJECT/$ENV/app (already set by Terraform)"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Run the CockroachDB schema: shared/sql/001_initial_schema.sql"
Write-Host "  2. Deploy services: .\deploy.ps1 -Action services"
Write-Host "  3. Register webhook URL in Stripe dashboard"
