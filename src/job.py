import random
import string

from src.status import Status

class JobModel:
    def __init__(self):
        self.job_id: str = ""
        self.status: str = Status.IN_PROGRESS
        self.files: list[str] = []
        self.completed: bool = False

class Job:
    def __init__(self):
        self.jobs: list[JobModel] = []

    def create_job(self) -> JobModel:
        job = JobModel()
        key1 = random.choice(string.ascii_lowercase)
        key2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
        job.job_id = key1 + key2
        self.jobs.append(job)
        return job

    def get_job(self, job_id: str) -> JobModel | None:
        for job in self.jobs:
            if job.job_id == job_id:
                return job
        return None

    def get_status(self, job_id: str) -> str | None:
        job = self.get_job(job_id)
        return job.status if job else None
