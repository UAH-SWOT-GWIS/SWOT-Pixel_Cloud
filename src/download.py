import earthaccess as ea
import asyncio

from upload import stream_to_s3
from websocket_connection import ConnectionManager, send_message
from job import JobModel
from status import Status
from utils.utils import callWithNonNoneArgs

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

async def download_data(
    short_name: str, granules: list[str] | None, date_range: list[str], 
    bounding_box: list[float] | None, version: str | None = None, 
    manager: ConnectionManager = None, job: JobModel = None
): 
    if bounding_box is None:
        bounding_box = bbox
    
    if not version:
        version = 2.0

    if not granules:
        job.status = Status.NO_GRANULES
        return
    
    pixc_result = []

    for granule in granules:
        result = await callWithNonNoneArgs(ea.search_data,short_name = short_name, 
                                        granule_name = '*'+granule+'*',
                                        temporal = tuple(date_range),
                                        bounding_box = tuple(bounding_box),
                                        version = version)
        pixc_result.append(result)

    # # Flatten the result list
    # pixc_result = [granule for sublist in pixc_result for granule in sublist]

    message = (
        f"Earth data search request name: {short_name}, granules: {granules}, "
        f"date_range: {date_range}, bounding_box: {bounding_box} found {len(pixc_result)} granules to download"
    )
    
    asyncio.create_task(send_message(message, broadcast=False, manager=manager))

    if not pixc_result:
        job.status = Status.NO_GRANULES
        return
    
    for pixc in pixc_result:
        for granule in pixc:
            if granule:
                stream_to_s3(granule,job,manager,auth)
