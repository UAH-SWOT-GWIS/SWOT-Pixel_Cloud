import requests
from datetime import datetime, timedelta

# Calculate current and 30 days ago dates
end_date = datetime.utcnow().date()
start_date = end_date - timedelta(days=30)

# Format dates as strings (e.g., "2025-04-24")
start_str = start_date.isoformat()
end_str = end_date.isoformat()

url = "http://localhost:8000/download?short_name=SWOT_L2_HR_PIXC_2.0"

# Query parameters
data = {
    "granules": [
        "147_210R",
        "147_209L",
        "147_209R",
        "466_100L"
    ],
    "date_range" : [start_str, end_str],
    "bounding_box" : [-84.56135835391053, 31.16490399933741, -84.3315612734074, 31.32566737314458],
    "version": "2.0"
}
print(data)

try:
    response = requests.post(url, json=data)
    response.raise_for_status()
    print(f"Success: {response.status_code}, Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
