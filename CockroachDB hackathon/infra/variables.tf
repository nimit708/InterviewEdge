variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-west-2"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "ledgermind"
}

# --- Networking (use existing VPC) ---
variable "vpc_id" {
  description = "Existing VPC ID to deploy into"
  type        = string
  default     = "vpc-0d94adc8c84ed52fe"
}

variable "subnet_ids" {
  description = "Existing subnet IDs (at least 2, in different AZs)"
  type        = list(string)
  default     = ["subnet-037a83e2816eedba5", "subnet-02367de8670ed90ce"]
  # eu-west-2a and eu-west-2b
}

# --- ECS ---
variable "api_cpu" {
  description = "CPU units for API task (1 vCPU = 1024)"
  type        = number
  default     = 512
}

variable "api_memory" {
  description = "Memory (MiB) for API task"
  type        = number
  default     = 1024
}

variable "agent_cpu" {
  description = "CPU units for Agent task"
  type        = number
  default     = 1024
}

variable "agent_memory" {
  description = "Memory (MiB) for Agent task"
  type        = number
  default     = 2048
}

variable "worker_cpu" {
  description = "CPU units for Worker task"
  type        = number
  default     = 256
}

variable "worker_memory" {
  description = "Memory (MiB) for Worker task"
  type        = number
  default     = 512
}

variable "api_desired_count" {
  description = "Number of API containers"
  type        = number
  default     = 2
}

# --- Domain ---
variable "domain_name" {
  description = "Domain name for the application (optional)"
  type        = string
  default     = ""
}

# --- Cognito ---
variable "cognito_callback_urls" {
  description = "Cognito OAuth callback URLs"
  type        = list(string)
  default     = ["http://localhost:3000"]
}

variable "cognito_logout_urls" {
  description = "Cognito OAuth logout URLs"
  type        = list(string)
  default     = ["http://localhost:3000"]
}


# --- GitHub ---
variable "github_access_token" {
  description = "GitHub personal access token for Amplify to access the repo"
  type        = string
  sensitive   = true
  default     = ""
}
