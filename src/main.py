from fastapi import FastAPI, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from download import download_data
from websocket_connection import ConnectionManager, connect
from job import JobModel, Job

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job = Job()  # Job instance
manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "Hello from SWOT"}

@app.post("/download")
async def download(
    background_tasks: BackgroundTasks, short_name: str, 
    granules: list[str] | None = None, date_range: list[str] | None = None, 
    bounding_box: list[float] | None = None, version: str | None = None):

    new_job: JobModel = job.create_job()
    background_tasks.add_task(download_data, short_name, granules, date_range, bounding_box, version, manager, new_job)
    
    return JSONResponse(content={
        "message": "success", 
        "status": "Downloading in progress", 
        "reference_id": new_job.job_id
    })

@app.websocket("/ws")
async def websocket_connect(websocket: WebSocket):
    await connect(websocket=websocket, manager=manager)

@app.get("/status/{uid}")
async def status(uid: str):
    job_status = job.get_status(uid)
    if job_status is None:
        return JSONResponse(content={"error": "Job not found"}, status_code=404)
    
    return JSONResponse(content={"status": job_status})
