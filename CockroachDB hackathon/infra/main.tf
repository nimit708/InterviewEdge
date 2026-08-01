# LedgerMind Infrastructure — Main Entry Point
# AWS Setup: VPC, ECS Fargate, ALB, SQS, Cognito, Secrets Manager

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
  }

  # Uncomment for remote state
  # backend "s3" {
  #   bucket = "ledgermind-terraform-state"
  #   key    = "infra/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "LedgerMind"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
