
output "ec2_sg_id" {
  description = "ID of the EC2 Security Group"
  value       = aws_security_group.ec2_sg.id
}

output "alb_sg_id" {
  description = "ID of the ALB Security Group"
  value       = aws_security_group.alb_sg.id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = [for subnet in aws_subnet.private : subnet.id]
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = [for subnet in aws_subnet.public : subnet.id]
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.app_alb.dns_name
}

output "application_url" {
  description = "URL to access the application via the Load Balancer"
  value       = "http://${aws_lb.app_alb.dns_name}"
}

output "s3_bucket_name" {
  description = "Name of the existing S3 bucket used for application data"
  # Value now comes from the data source lookup
  value = data.aws_s3_bucket.app_data.bucket
}