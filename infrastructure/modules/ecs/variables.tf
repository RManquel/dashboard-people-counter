variable "project_name"      { type = string }
variable "environment"       { type = string }
variable "aws_region"        { type = string }
variable "vpc_id"            { type = string }
variable "private_subnets"   { type = list(string) }
variable "alb_sg_id"         { type = string }
variable "target_group_arn"  { type = string }
variable "backend_image"     { type = string }
variable "frontend_image"    { type = string }
variable "database_url"      { type = string; sensitive = true }
