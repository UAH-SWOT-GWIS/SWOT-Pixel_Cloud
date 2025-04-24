#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data ) 2>&1

yum update -y
yum install -y docker
yum install -y git

# Start Docker and add ubuntu user to docker group
sudo service docker start
sudo usermod -aG docker ec2-user
newgrp docker

# Install CloudWatch Agent
yum install -y amazon-cloudwatch-agent

# Create CloudWatch config
cat <<EOF > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/cloud-init.log",
            "log_group_name": "/ec2/fastapi/cloud-init",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/user-data.log",
            "log_group_name": "/ec2/fastapi/userdata",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# Start the CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json \
  -s

cd /home/ec2-user/
git clone https://github.com/UAH-SWOT-GWIS/SWOT-Pixel_Cloud.git
cd SWOT-Pixel_Cloud

chown -R ec2-user:ec2-user /home/ec2-user/SWOT-Pixel_Cloud
# Run app with nohup on port 8000
# nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
docker build -t swot .
docker run -d --name swot-container -p 8000:8000 swot  -e APP_ENV=production \
      -e EARTHDATA_USERNAME = ${var.earthdata_username} \
      -e EARTHDATA_PASSWORD = ${var.earthdata_password} \
      -e S3_BUCKET = ${var.s3_bucket}
      swot