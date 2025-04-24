#!/bin/bash
exec > >(tee /var/log/user-data.log|logger -t user-data ) 2>&1

yum update -y
yum install -y docker
yum install -y git
yum install python3 -y
pip install requests

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
            "log_group_name": "/ec2/swot-api/{instance_id}",
            "log_stream_name": "cloud-init.log"
          },
          {
            "file_path": "/var/log/user-data.log",
            "log_group_name": "/ec2/swot-api/{instance_id}",
            "log_stream_name": "user-data.log"
          },
          {
            "file_path": "/var/lib/docker/containers/*/*.log",
            "log_group_name": "/ec2/swot-api/{instance_id}",
            "log_stream_name": "app.log"
          },
          {
            "file_path": "/var/log/swot-api_cron.log",
            "log_group_name": "/ec2/swot-api/{instance_id}",
            "log_stream_name": "cron.log"
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
chmod +x /home/ec2-user/SWOT-Pixel_Cloud/schedule.py
echo "0 0 1 */1 * /usr/bin/python3 /home/ec2-user/SWOT-Pixel_Cloud/schedule.py >> /var/log/swot-api_cron.log 2>&1" | crontab -

export EARTHDATA_USERNAME="${earthdata_username}"
export EARTHDATA_PASSWORD="${earthdata_password}"
export S3_BUCKET="${s3_bucket}"

# Run app with nohup on port 8000
# nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
docker build -t swot .
docker run -d --name swot-container -p 8000:8000 \
  -e APP_ENV=production \
  -e EARTHDATA_USERNAME="${earthdata_username}" \
  -e EARTHDATA_PASSWORD="${earthdata_password}" \
  -e S3_BUCKET="${s3_bucket}" \
  -e PYTHONUNBUFFERED=1 \
  swot