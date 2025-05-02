import logging
import earthaccess as ea
from upload import stream_to_s3
logger = logging.getLogger(__name__)

auth = ea.login(strategy="environment")

multipolygon = [
    [
        [
            [-84.561358353910535, 31.180958403382959],
            [-84.560026431680228, 31.325667373144579],
            [-84.331561273407402, 31.320961052712427],
            [-84.379678035151116, 31.164903999337412],
            [-84.559788880227046, 31.170500089680807],
            [-84.55997255314405, 31.170503573102543],
            [-84.560523572086467, 31.170514021797548],
            [-84.560523572086467, 31.170514021797548],
            [-84.561358353910535, 31.180958403382959]
        ]
    ]
]

# Extract lat/lon values
lons, lats = zip(*multipolygon[0][0])
bbox = [min(lons), min(lats), max(lons), max(lats)]

def download_data(data): 
    if data.get('bounding_box') is None:
        data['bounding_box'] = bbox
    
    if data.get('version') is None:
        data['version'] = 2.0
    
    pixc_result = []
    
    for granule in data.get('granules'):
        try:
            result = ea.search_data(short_name=data.get('short_name'), granule_name='*'+granule+'*',
                                temporal=tuple(data.get('date_range')),
                                bounding_box=tuple(data.get('bounding_box')),
                                version=data.get('version'))
            pixc_result.append(result)
        except IndexError:
            continue
        
    if not pixc_result:
        logger.info('No PIXC files found')
        return
    
    for pixc in pixc_result:
        for granule in pixc:
            if granule:
                stream_to_s3(granule, auth)
