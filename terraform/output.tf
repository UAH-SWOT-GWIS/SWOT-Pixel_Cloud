
output "public_dns" {
  value = aws_instance.swot_web.public_dns
  description = "Public DNS of the EC2 instance"
}
output "public_ip" {
  value = aws_instance.swot_web.public_ip
  description = "Public IP of the EC2 instance"
}
output "url" {
  value = "http://${aws_instance.swot_web.public_ip}:8000"
  description = "Public IP of the EC2 instance"
}