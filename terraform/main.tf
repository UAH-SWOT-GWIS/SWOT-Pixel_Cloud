#provider & Region

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_security_group" "swot_sg" {
  name_prefix = "fastapi-sg-"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#Configure the resource
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners  	= ["amazon"]

  filter {
	name   = "name"
	values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_default_vpc" "default" {
  tags = {
    Name = "Default VPC"
  }
}

resource "aws_instance" "swot_web" {
  ami       	= data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  associate_public_ip_address = true
  key_name               = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.swot_sg.id]
  user_data              = file("user_data.sh")
  tags = {
    Name = "SWOT"
  }
}