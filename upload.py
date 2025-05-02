from datetime import datetime
import traceback
import logging

import boto3

from config import s3BucketName, aws_access_key_id, aws_secret_access_key
from process import process_shp
logger = logging.getLogger(__name__)

s3 = boto3.client("s3",aws_access_key_id=aws_access_key_id, 
                  aws_secret_access_key=aws_secret_access_key)

def upload_stream(download_urls, meta_data, auth):
    if not download_urls:
        logger.info(f"No download links found")
        return
    
    elif not auth:
        logger.warning(f"Invalid auth credentials")
        return
    
    s3_dir = f"{meta_data.get('pass', 'unknown')}/{meta_data.get('tile', 'unknown')}/{meta_data.get('date', 'unknown')}/"
    
    logger.info(f"Downloading urls {download_urls}")
    
    for url in download_urls:
        file_name = url.split('/')[-1]
        logger.info(f"Downloading {file_name} from {url}")
        
        # Stream the file directly to S3
        if file_name.endswith('.json'):
            s3_location = s3_dir + 'meta' + '/' + file_name
        else:
            s3_location = s3_dir + file_name
        
        try:
            response = fetch_file(url,auth)
            if file_name.endswith('.nc'):
                with open(file_name, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=128):
                        fd.write(chunk)
            			
                # Now start a new thread that does the shapefile processing and upload
                process_shp(file_name, meta_data)
            
            s3.upload_fileobj(response.raw, s3BucketName, s3_location)
            
            logger.info(f"Uploaded {file_name} to s3://{s3BucketName}/{s3_location}")
            
        except Exception as e:
            logger.error(f"Failed to upload {file_name}: {str(e)}")
            logger.info(traceback.format_exc())

def fetch_file(url, auth):
    session = auth.get_session()
    response = session.get(url, stream=True)
    response.raise_for_status()
    return response

def stream_to_s3(granule, auth):
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
    
    upload_stream(download_urls, meta_data, auth)
    
