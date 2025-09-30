# These schemas handle asynchronous job processing for story generation in your Choose Your Own Adventure application.
from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# Workflow Overview:
# User Request → Create Job → Background Processing → Job Completion
#      ↓              ↓               ↓                    ↓
# StoryJobCreate → StoryJobResponse → StoryJobResponse → Story Ready
#    (theme)      (pending status)   (processing)      (completed + story_id)


# Purpose: Base schema containing the core data needed to create a story job
# theme: str: The theme/prompt for AI story generation (e.g., "space pirates", "medieval quest")
# Example:
# {
#   "theme": "underwater adventure with mermaids"
# }
class StoryJobBase(BaseModel):
    theme: str


# Purpose: Complete job status response for tracking story generation progress
# job_id: int: Unique identifier for this specific job
# status: str: Current job state (e.g., "pending", "processing", "completed", "failed")
# story_id: Optional[int] = None: ID of generated story (only set when job completes successfully)
# error: Optional[str] = None: Error message if job failed
# created_at: datetime: When the job was started
# completed_at: Optional[datetime] = None: When the job finished (null if still running)
# Config: from_attributes = True: Allows creation from SQLAlchemy model attributes
# Example: (Job in progress):
# {
#   "job_id": 12345,
#   "status": "processing",
#   "story_id": null,
#   "error": null,
#   "created_at": "2025-09-29T10:30:00Z",
#   "completed_at": null
# }
# Example JSON (Completed job):
# {
#   "job_id": 12345,
#   "status": "completed",
#   "story_id": 567,
#   "error": null,
#   "created_at": "2025-09-29T10:30:00Z",
#   "completed_at": "2025-09-29T10:32:15Z"
# }
class StoryJobResponse(BaseModel):
    job_id: str
    status: str
    story_id: Optional[int] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StoryJobCreate(StoryJobBase):
    pass