# Use existing default VPC and subnets — no new network resources needed

data "aws_vpc" "default" {
  id = var.vpc_id
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [var.vpc_id]
  }
}

locals {
  # Pick 2 subnets in different AZs for ALB (minimum requirement)
  subnet_ids = var.subnet_ids
}
