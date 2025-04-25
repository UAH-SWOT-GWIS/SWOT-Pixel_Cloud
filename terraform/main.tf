terraform {
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

resource "aws_key_pair" "deployer" {
  key_name   = var.key_name
  public_key = file("~/.ssh/id_rsa.pub")
}

locals {
  project_name = var.project_name
  common_tags = {
    Project     = local.project_name
    ManagedBy   = "Terraform"
    Environment = "Dev"
  }
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-vpc"
  })
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-igw"
  })
}

resource "aws_subnet" "public" {
  vpc_id            = aws_vpc.main.id
  count             = length(var.public_subnet_cidrs)
  cidr_block        = var.public_subnet_cidrs[count.index]
  map_public_ip_on_launch = false
  availability_zone       = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-public-subnet-${count.index + 1}"
    Tier = "Public"
  })
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-public-rt"
  })
}

resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-private-subnet-${count.index + 1}"
    Tier = "Private"
  })
}

# NAT Gateway
resource "aws_eip" "nat" {
  count  = 1 # Single NAT GW for simplicity
  domain = "vpc"

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-nat-eip-${count.index + 1}"
  })
  depends_on = [aws_internet_gateway.igw]
}

resource "aws_nat_gateway" "nat" {
  count         = 1 # Corresponds to aws_eip.nat count
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id # NAT GW in public subnet

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-nat-gw-${count.index + 1}"
  })
  depends_on = [aws_internet_gateway.igw]
}

# Private Route Table
resource "aws_route_table" "private" {
  count  = 1
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[count.index].id
  }

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-private-rt-${count.index + 1}"
  })
}

resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}

resource "aws_security_group" "alb_sg" {
  name        = "${local.project_name}-alb-sg"
  description = "Allow HTTP inbound traffic to ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(local.common_tags, { Name = "${local.project_name}-alb-sg" })
}

resource "aws_security_group" "ec2_sg" {
  name        = "${local.project_name}-ec2-sg"
  description = "Allow App traffic from ALB and SSH"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Allow App traffic from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }
  ingress {
    description = "Allow SSH from allowed CIDR"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = merge(local.common_tags, { Name = "${local.project_name}-ec2-sg" })
}

resource "aws_iam_role" "ec2_role" {
  name = "${local.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
  })
  tags = merge(local.common_tags, {
    Name = "${local.project_name}-ec2-role"
  })
}

data "aws_s3_bucket" "app_data" {
  bucket = var.s3_bucket
}

# Granular S3 Policy
resource "aws_iam_policy" "s3_access" {
  name        = "${local.project_name}-s3-access-policy"
  description = "Policy granting necessary S3 permissions for the app"

  # Reference the existing bucket via the data source
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:ListBucket"
        ],
        Resource = [
          data.aws_s3_bucket.app_data.arn # <-- UPDATED
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ],
        Resource = [
          "${data.aws_s3_bucket.app_data.arn}/*" # <-- UPDATED
        ]
      }
    ]
  })

  tags = merge(local.common_tags, {})
}


resource "aws_iam_role_policy_attachment" "s3_policy_attach" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_policy_attach" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_role_policy_attachment" "ssm_policy_attach" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "instance_profile" {
  name = "swot-instance-profile"
  role = aws_iam_role.ec2_role.name
  tags = merge(local.common_tags, {})
}


#Configure the resource
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners  	= ["amazon"]

  filter {
	name   = "name"
	values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

data "template_file" "user_data" {
  template = file("${path.module}/user_data.sh.tpl")

  vars = {
    earthdata_username = var.earthdata_username
    earthdata_password = var.earthdata_password
    s3_bucket          = var.s3_bucket
    project_name       = local.project_name
    aws_region         = var.aws_region
  }
}

resource "aws_launch_template" "app_lt" {
  name_prefix   = "${local.project_name}-lt-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  iam_instance_profile {
    name = aws_iam_instance_profile.instance_profile.name
  }

  user_data = base64encode(data.template_file.user_data.rendered)

  tag_specifications {
    resource_type = "instance"
    tags          = merge(local.common_tags, { Name = "${local.project_name}-instance" })
  }
  tag_specifications {
    resource_type = "volume"
    tags          = merge(local.common_tags, { Name = "${local.project_name}-volume" })
  }

  tags = merge(local.common_tags, { Name = "${local.project_name}-launch-template" })

  lifecycle { create_before_destroy = true }
}

resource "aws_autoscaling_group" "app_asg" {
  name_prefix         = "${local.project_name}-asg-"
  vpc_zone_identifier = [for subnet in aws_subnet.private : subnet.id]

  launch_template {
    id      = aws_launch_template.app_lt.id
    version = "$Latest"
  }

  min_size          = 1
  max_size          = 1
  desired_capacity  = 1
  health_check_type = "ELB"
  # Keep longer grace period for debugging if needed, otherwise revert to 300
  health_check_grace_period = 1800 # Or 300

  target_group_arns = [aws_lb_target_group.app_tg.arn]

  tag {
    key                 = "Name"
    value               = "${local.project_name}-instance"
    propagate_at_launch = true
  }
  # Add other tags as needed and propagate
  dynamic "tag" {
    for_each = local.common_tags
    content {
      key                 = tag.key
      value               = tag.value
      propagate_at_launch = true
    }
  }

  lifecycle { create_before_destroy = true }
  depends_on = [aws_lb.app_alb]
}

#--------------------------------------
# Application Load Balancer (ALB) - Added idle_timeout
#--------------------------------------
resource "aws_lb" "app_alb" {
  name               = "${local.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [for subnet in aws_subnet.public : subnet.id]

  enable_deletion_protection = false
  idle_timeout               = 300 # Keep increased timeout if needed

  tags = merge(local.common_tags, { Name = "${local.project_name}-alb" })
}

resource "aws_lb_target_group" "app_tg" {
  name        = "${local.project_name}-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  health_check {
    enabled             = true
    path                = "/" # Ensure your app has a GET / route that returns 200 OK quickly
    port                = "traffic-port"
    protocol            = "HTTP"
    matcher             = "200-399"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }

  tags = merge(local.common_tags, { Name = "${local.project_name}-target-group" })
  lifecycle { create_before_destroy = true }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}