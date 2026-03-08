variable "project_name" {
  description = "Project name used as prefix for all resources"
  type        = string
  default     = "stadium"
}

variable "environment" {
  description = "Deployment environment (production, staging)"
  type        = string
  default     = "production"
}

variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "stadium_db"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "stadium"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "backend_image" {
  description = "Docker image URI for the FastAPI backend"
  type        = string
  # e.g. 123456789012.dkr.ecr.us-east-1.amazonaws.com/stadium-backend:latest
}

variable "frontend_image" {
  description = "Docker image URI for the React frontend"
  type        = string
}
