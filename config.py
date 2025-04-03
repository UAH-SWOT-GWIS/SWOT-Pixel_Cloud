import os

from dotenv import load_dotenv

load_dotenv()

s3BucketName = os.environ.get('S3_BUCKET')
s3ObjectUrl = os.environ.get('S3_OBJECT_URL')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
username = os.environ.get('EARTHDATA_USERNAME')