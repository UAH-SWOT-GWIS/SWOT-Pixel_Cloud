variable "instance_type" {
  description = "EC2 instance type for the application"
  type    	  = string
  default 	  = "t3.micro"
}

variable "aws_region" {
  description = "AWS region to deploy resources into."
  type    	= string
  default 	= "us-east-1"
}

variable "key_name" {
  default = "Name of the AWS key pair to use for SSH access. Must exist in the AWS region."
  type    = string
}

variable "earthdata_username" {
  description = "earthdata username"
  type    	  = string
  sensitive   = true
}

variable "earthdata_password" {
  description = "earthdata password"
  type    	  = string
  sensitive   = true
}

variable "s3_bucket" {
  description = "Name for the S3 bucket to store application data. Needs to be globally unique."
  type        = string
}

# --- Helper ---
data "aws_availability_zones" "available" {
  state = "available"
}

variable "allowed_ssh_cidr" {
  description = "CIDR block allowed to SSH into the EC2 instances."
  type        = list(string)
  default     = ["0.0.0.0/0"] # Still defaulting here, but can be overridden via tfvars or .env
}

variable "project_name" {
  description = "A name for the project to prefix resources."
  type        = string
  default     = "swot-fastapi"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets in different AZs."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "List of CIDR blocks for private subnets in different AZs."
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24"]
}