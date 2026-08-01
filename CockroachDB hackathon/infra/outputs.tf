# Outputs — values needed after terraform apply

output "vpc_id" {
  description = "VPC ID (existing)"
  value       = var.vpc_id
}

# API Gateway
output "api_url" {
  description = "API Gateway URL (public endpoint for frontend + Stripe)"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

# Cognito
output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Cognito App Client ID"
  value       = aws_cognito_user_pool_client.dashboard.id
}

output "cognito_domain" {
  description = "Cognito hosted UI domain"
  value       = "https://${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com"
}

# SQS
output "sqs_payment_events_url" {
  description = "SQS Payment Events Queue URL"
  value       = aws_sqs_queue.payment_events.url
}

output "sqs_agent_tasks_url" {
  description = "SQS Agent Tasks Queue URL"
  value       = aws_sqs_queue.agent_tasks.url
}

# ECR
output "ecr_api_url" {
  description = "ECR repository URL for API"
  value       = aws_ecr_repository.api.repository_url
}

output "ecr_worker_url" {
  description = "ECR repository URL for Worker"
  value       = aws_ecr_repository.worker.repository_url
}

output "ecr_agent_url" {
  description = "ECR repository URL for Agent"
  value       = aws_ecr_repository.agent.repository_url
}

# ECS
output "ecs_cluster_name" {
  description = "ECS Cluster name"
  value       = aws_ecs_cluster.main.name
}

# Secrets Manager ARNs
output "secret_cockroachdb_arn" {
  description = "Secrets Manager ARN for CockroachDB credentials"
  value       = aws_secretsmanager_secret.cockroachdb_url.arn
}

output "secret_stripe_arn" {
  description = "Secrets Manager ARN for Stripe credentials"
  value       = aws_secretsmanager_secret.stripe.arn
}

output "secret_bedrock_arn" {
  description = "Secrets Manager ARN for Bedrock config"
  value       = aws_secretsmanager_secret.bedrock.arn
}

# Amplify
output "amplify_app_id" {
  description = "Amplify App ID"
  value       = aws_amplify_app.frontend.id
}

output "amplify_default_domain" {
  description = "Amplify default domain"
  value       = aws_amplify_app.frontend.default_domain
}

# Stripe Webhook URL (register this in Stripe dashboard)
output "stripe_webhook_url" {
  description = "URL to register as Stripe webhook endpoint"
  value       = "${aws_apigatewayv2_api.main.api_endpoint}/api/v1/webhook/stripe"
}
