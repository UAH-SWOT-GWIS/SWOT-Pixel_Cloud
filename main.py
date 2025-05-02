import sys
import logging
from datetime import date, datetime, timedelta, timezone
from config import short_name, granule_list, data_ver
from download import download_data
logger = logging.getLogger(__name__)

n = len(sys.argv)
if (n == 1):
    # No arguments, use search range of past 30 days
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=30)
else:
    if (n==3):
        try:
            start_date = date.fromisoformat(sys.argv[1])
            end_date = date.fromisoformat(sys.argv[2])
        except ValueError:
            sys.exit("Start/end dates must be in YYYY-MM-DD format")
        
        if (start_date > end_date) or (end_date > datetime.now(timezone.utc).date()):
            sys.exit("End date cannot be before start date, oin the future")
    elif (n == 2):
        if sys.argv[1] in ["-h", "help", "-help"]:
            print("Accepted command format: python3 main.py start_date <optional: end_date>")
            print("Dates must be in YYY-MM-DD format to be accepted")
            sys.exit(0)
        else:
            try:
                start_date = date.fromisoformat(sys.argv[1])
                end_date = datetime.now(timezone.utc).date()
            except ValueError:
                sys.exit("Start date must be in YYYY-MM-DD format")
            
            if start_date > end_date:
                sys.exit("Start date must come before today's date")
    else:
        print("Only up to 2 commands allowed: start_date <optional: end_date>")
        print("For more details run: python3 main.py -help")
        sys.exit(0)

today_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
logging.basicConfig(filename=f"logs/{today_str}.log", level=logging.INFO)
start_str = start_date.isoformat()
end_str = end_date.isoformat()

data = {
    'granules': granule_list,
    'date_range': [start_str, end_str],
    'bounding_box': [-84.56135835391053, 31.16490399933741, -84.3315612734074, 31.32566737314458],
    'short_name': short_name,
    'version': data_ver
    }

# Send the request to the download script
logger.info('Starting script')
download_data(data)
