# ECS Cluster and Services (3 services: API, Worker, Agent)

resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-cluster"
  }
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${var.project_name}-${var.environment}/api"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}-${var.environment}/worker"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "agent" {
  name              = "/ecs/${var.project_name}-${var.environment}/agent"
  retention_in_days = 30
}

# --- FastAPI Service (handles API + Stripe webhook + CSV import) ---

resource "aws_ecs_task_definition" "api" {
  family                   = "${var.project_name}-${var.environment}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name  = "api"
      image = "${aws_ecr_repository.api.repository_url}:latest"

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "ENVIRONMENT", value = var.environment },
        { name = "SQS_PAYMENT_QUEUE_URL", value = aws_sqs_queue.payment_events.url },
        { name = "SQS_AGENT_QUEUE_URL", value = aws_sqs_queue.agent_tasks.url },
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.cockroachdb_url.arn}:url::"
        },
        {
          name      = "STRIPE_SECRET_KEY"
          valueFrom = "${aws_secretsmanager_secret.stripe.arn}:secret_key::"
        },
        {
          name      = "STRIPE_WEBHOOK_SECRET"
          valueFrom = "${aws_secretsmanager_secret.stripe.arn}:webhook_secret::"
        },
        {
          name      = "COGNITO_USER_POOL_ID"
          valueFrom = "${aws_secretsmanager_secret.app.arn}:cognito_user_pool_id::"
        },
        {
          name      = "COGNITO_APP_CLIENT_ID"
          valueFrom = "${aws_secretsmanager_secret.app.arn}:cognito_client_id::"
        },
        {
          name      = "BEDROCK_MODEL_ID"
          valueFrom = "${aws_secretsmanager_secret.bedrock.arn}:model_id::"
        },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.api.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "api"
        }
      }

      essential = true
    }
  ])
}

resource "aws_ecs_service" "api" {
  name            = "${var.project_name}-${var.environment}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  # Register with Cloud Map for API Gateway discovery
  service_registries {
    registry_arn = aws_service_discovery_service.api.arn
  }
}

# --- Ingestion Worker (polls SQS for payment events) ---

resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-${var.environment}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name    = "worker"
      image   = "${aws_ecr_repository.worker.repository_url}:latest"
      command = ["python", "-m", "worker.main"]

      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "SQS_QUEUE_URL", value = aws_sqs_queue.payment_events.url },
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.cockroachdb_url.arn}:url::"
        },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.worker.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "worker"
        }
      }

      essential = true
    }
  ])
}

resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-${var.environment}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }
}

# --- LedgerMind Agent (polls SQS for agent tasks, calls Bedrock) ---

resource "aws_ecs_task_definition" "agent" {
  family                   = "${var.project_name}-${var.environment}-agent"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.agent_cpu
  memory                   = var.agent_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name    = "agent"
      image   = "${aws_ecr_repository.agent.repository_url}:latest"
      command = ["python", "-m", "agent.service"]

      environment = [
        { name = "AWS_REGION", value = var.aws_region },
        { name = "SQS_AGENT_QUEUE_URL", value = aws_sqs_queue.agent_tasks.url },
        { name = "SQS_PAYMENT_QUEUE_URL", value = aws_sqs_queue.payment_events.url },
      ]

      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = "${aws_secretsmanager_secret.cockroachdb_url.arn}:url::"
        },
        {
          name      = "BEDROCK_MODEL_ID"
          valueFrom = "${aws_secretsmanager_secret.bedrock.arn}:model_id::"
        },
        {
          name      = "BEDROCK_EMBEDDING_MODEL_ID"
          valueFrom = "${aws_secretsmanager_secret.bedrock.arn}:embedding_model_id::"
        },
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.agent.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "agent"
        }
      }

      essential = true
    }
  ])
}

resource "aws_ecs_service" "agent" {
  name            = "${var.project_name}-${var.environment}-agent"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.agent.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }
}
