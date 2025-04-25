from datetime import datetime
import traceback

import asyncio
import boto3

from config import s3BucketName, aws_access_key_id, aws_secret_access_key
from websocket_connection import ConnectionManager,send_message
from job import JobModel
from status import Status

s3 = boto3.client("s3",aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key)

def upload_stream(download_urls, meta_data, job: JobModel, manager: ConnectionManager = None,stream_in_chunks = False,auth = None):
    if not download_urls:
        print(f"No download links found")
        return
    
    elif not auth:
        print(f"Invalid auth credentials")
        return
    
    elif stream_in_chunks:
        #implementation needed to download in chunks, if the file_size is large; 
        # skipping this implementation as all SWOT data is less than 700MB ~approximately
        print("chunks stream")
        return
    
    s3_dir = f"{meta_data.get('pass', 'unknown')}/{meta_data.get('tile', 'unknown')}/{meta_data.get('date', 'unknown')}/"

    # loop = asyncio.get_running_loop()
    
    print(f"downloading urls {download_urls}")

    for url in download_urls:
        file_name = url.split('/')[-1]
        print(f"Downloading {file_name} from {url}")

        asyncio.run(send_message(f"Downloading {file_name} from {url}", 
                                               broadcast=False, manager=manager))

        # Stream the file directly to S3
        if file_name.endswith('.json'):
            s3_location = s3_dir + 'meta' + '/' + file_name
        else:
            s3_location = s3_dir + file_name
        
        try:
            response = fetch_file(url,auth)
            s3.upload_fileobj(response.raw, s3BucketName, s3_location)
            
            print(f"Uploaded {file_name} to s3://{s3BucketName}/{s3_location}")
            asyncio.run(send_message(f"Uploaded {file_name} to s3://{s3BucketName}/{s3_location}", broadcast=False, manager=manager))
            job.status = Status.JOB_COMPLETE

        except Exception as e:
            print(f"Failed to upload {file_name}: {str(e)}")
            traceback.print_exc()
            asyncio.run(send_message(f"Error uploading {file_name}: {str(e)}", broadcast=False, manager=manager))
            job.status = Status.ERROR

        
def fetch_file(url, auth):
    session = auth.get_session()
    response = session.get(url, stream=True)
    response.raise_for_status()
    return response

def stream_to_s3(granule, job: JobModel, manager: ConnectionManager = None,auth=None):
    granule_umm = granule.get('umm', {})
    granule_ur = granule_umm.get('GranuleUR', '')

    info = granule_umm.get('DataGranule', {}).get('ArchiveAndDistributionInformation', [])
    data = [float(x['Size']) for x in info if x.get('Name') == granule_ur + '.nc']
    file_size = data[0] if data else 0.0

    download_urls = granule.data_links()

    granule_track = granule_umm.get('SpatialExtent', {}).get('HorizontalSpatialDomain', {}).get('Track', {}).get('Passes', [])
    pass_no = granule_track[0].get('Pass', 'Unknown') if granule_track else 'Unknown'
    tile = granule_track[0].get('Tiles', ['Unknown'])[0] if granule_track else 'Unknown'
    
    granule_date_range = granule_umm.get('TemporalExtent', {}).get('RangeDateTime', {})
    timestamp = granule_date_range.get('EndingDateTime', '')
    
    date = 'Unknown'
    if timestamp:
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
            date = dt.date()
        except ValueError:
            pass  # Handle incorrect date format gracefully

    stream_chunks = False  # Enable chunked streaming for large files

    meta_data_urls = granule._filter_related_links("EXTENDED METADATA")
    meta_json_urls = [url for url in meta_data_urls if url.startswith("http") and url.endswith(".json")]
    
    if meta_json_urls:
        download_urls.append(meta_json_urls[0])

    meta_data = {
        "pass": str(pass_no),
        "tile": str(tile),
        "date": str(date),
        "urls": download_urls
    }
    asyncio.run(send_message(meta_data, broadcast=True, manager=manager))

    upload_stream(download_urls, meta_data, job, manager, stream_chunks,auth)
    