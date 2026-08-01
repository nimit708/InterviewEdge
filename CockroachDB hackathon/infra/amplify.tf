# AWS Amplify — Frontend React Dashboard Hosting
# Connected to GitHub for auto-deploy on push

resource "aws_amplify_app" "frontend" {
  name       = "${var.project_name}-${var.environment}-dashboard"
  repository = "https://github.com/nimit708/LedgerMind"

  # GitHub access token needed — set via variable
  access_token = var.github_access_token

  # Build settings for Vite + React (frontend is in /frontend dir)
  build_spec = <<-EOT
    version: 1
    frontend:
      phases:
        preBuild:
          commands:
            - cd frontend
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: frontend/dist
        files:
          - '**/*'
      cache:
        paths:
          - frontend/node_modules/**/*
  EOT

  # Environment variables for the frontend build
  environment_variables = {
    VITE_API_URL              = aws_apigatewayv2_api.main.api_endpoint
    VITE_COGNITO_USER_POOL_ID = aws_cognito_user_pool.main.id
    VITE_COGNITO_CLIENT_ID    = aws_cognito_user_pool_client.dashboard.id
    VITE_COGNITO_REGION       = var.aws_region
  }

  # SPA rewrite rule
  custom_rule {
    source = "/<*>"
    target = "/index.html"
    status = "200"
  }

  custom_rule {
    source = "</^[^.]+$|\\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json)$)([^.]+$)/>"
    target = "/index.html"
    status = "200"
  }
}

# Branch — main (auto-deploy on push)
resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = "main"
  stage       = var.environment == "prod" ? "PRODUCTION" : "DEVELOPMENT"

  enable_auto_build = true

  environment_variables = {
    VITE_ENVIRONMENT = var.environment
  }
}
