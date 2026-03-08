terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── VPC ──────────────────────────────────────────────────────────────
module "vpc" {
  source = "./modules/vpc"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

# ── ALB ──────────────────────────────────────────────────────────────
module "alb" {
  source = "./modules/alb"

  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.vpc.vpc_id
  public_subnets = module.vpc.public_subnet_ids
}

# ── RDS PostgreSQL ────────────────────────────────────────────────────
module "rds" {
  source = "./modules/rds"

  project_name     = var.project_name
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  private_subnets  = module.vpc.private_subnet_ids
  db_name          = var.db_name
  db_username      = var.db_username
  db_password      = var.db_password
  ecs_sg_id        = module.ecs.ecs_sg_id
}

# ── ECS Fargate ───────────────────────────────────────────────────────
module "ecs" {
  source = "./modules/ecs"

  project_name     = var.project_name
  environment      = var.environment
  aws_region       = var.aws_region
  vpc_id           = module.vpc.vpc_id
  private_subnets  = module.vpc.private_subnet_ids
  alb_sg_id        = module.alb.alb_sg_id
  target_group_arn = module.alb.target_group_arn

  backend_image  = var.backend_image
  frontend_image = var.frontend_image

  database_url = "postgresql+asyncpg://${var.db_username}:${var.db_password}@${module.rds.db_endpoint}/${var.db_name}"
}
