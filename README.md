
# FastAPI EarthData Downloader

This project is a FastAPI-based application designed to automate the downloading of EarthData (e.g., SWOT satellite data) and store it in an Amazon S3 bucket.

## Features

- Fetches EarthData files using EarthData credentials
- Securely uploads data to Amazon S3
- Easily deployable with Docker
- Supports environment configuration via `.env` file

## 🛠️ Requirements

- Docker
- AWS credentials with permissions to access S3
- EarthData account

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/UAH-SWOT-GWIS/SWOT-Pixel_Cloud.git
cd SWOT-Pixel_Cloud
```

### 2. Fill in the `.env` file

Create a `.env` file in the root directory with the following format:

```
EARTHDATA_USERNAME=your_earthdata_username
EARTHDATA_PASSWORD=your_earthdata_password

AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

S3_BUCKET=your_s3_bucket_name
S3_OBJECT_URL=https://your_s3_bucket.s3.amazonaws.com
```

> Make sure the `.env` file is listed in `.gitignore` to avoid exposing sensitive credentials.

---

## 🚀 Run the App with Docker

```bash
docker build -t swot .
docker run --env-file .env -p 8000:8000 --name swot-fastapi swot
```

Once the container is running, access the app at: [http://localhost:8000](http://localhost:8000)

Swagger Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📬 API Endpoints

### `GET /`

Health check route.

### `POST /download`

Triggers the download process and uploads to S3.

Sample Request :  http://localhost:8000/download?short_name=SWOT_L2_HR_PIXC_2.0
Sample Request body:
```json
{
    "granules": [
        "147_210R",
        "147_209L",
        "147_209R",
        "466_100L"
    ],
    "date_range" : ["2025-04-01", "2025-04-28"],
    "bounding_box" : [-84.56135835391053, 31.16490399933741, -84.3315612734074, 31.32566737314458],
    "version": "2.0"
}
```
version, bounding_box are optional. Default the bounding box values are [-84.56135835391053, 31.16490399933741, -84.3315612734074, 31.32566737314458] and default version is 2.0

Sample Response:
```json
{
    "message": "success",
    "status": "Downloading in progress",
    "reference_id": "bx3lnb98"
}
```
### `Websocket`

Provides real time updates to the client if connected
Sample Request : ws://localhost:8000/ws

### `GET /status`

Sample Request: http://localhost:8000/status/{reference_id from post request}

Sample Response:
```json
{
    "status": "In Progress"
}
```
#### Available status
Not Available -if the job reference is not available
In Progress - if the downloading is in progress
No granules found - if no granules to download
Completed - if the download & upload gets completed
Error Occurred - if request failed due to erros
