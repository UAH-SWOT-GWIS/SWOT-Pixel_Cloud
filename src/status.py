from enum import Enum

class Status(str, Enum):
    NOT_AVAILABLE = "Not Available"
    IN_PROGRESS = "In Progress"
    NO_GRANULES = "No granules found"
    JOB_COMPLETE = "Completed"
    ERROR = "Error Occurred"