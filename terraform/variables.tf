variable "instance_type" {
  description = "EC2 instance type"
  type    	= string
  default 	= "t2.micro"
}

variable "aws_region" {
  description = "AWS region to deploy into"
  type    	= string
  default 	= "us-east-1"
}
variable "key_name" {
  default = "fastapi-key"
}
variable "earthdata_username" {
  description = "earthdata username"
  type    	= string
  default 	= ""
}
variable "earthdata_password" {
  description = "earthdata password"
  type    	= string
  default 	= ""
}
variable "s3_bucket" {
  description = "bucket name"
  type = string
}