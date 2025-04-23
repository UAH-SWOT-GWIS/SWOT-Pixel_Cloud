#!/bin/bash
apt update -y
apt install -y docker.io git

# Start Docker and add ubuntu user to docker group
systemctl start docker
systemctl enable docker
usermod -aG docker ubuntu

cd /home/ubuntu
git clone https://github.com/UAH-SWOT-GWIS/SWOT-Pixel_Cloud.git swot
cd swot

# Run app with nohup on port 8000
# nohup venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
docker build -t swot .
docker run -d --name swot-container -p 8000:8000 swot  -e APP_ENV=production \
      -e EARTHDATA_USERNAME = ${var.earthdata_username} \
      -e EARTHDATA_PASSWORD = ${var.earthdata_password} \
      -e S3_BUCKET = ${var.s3_bucket}
      swot