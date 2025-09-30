import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Cookie, Response, Depends
from sqlalchemy.orm import Session

from db.database import get_db, SessionLocal
from models.story import Story, StoryNode
from models.job import StoryJob
from schemas.story import CompleteStoryResponse, CompleteStoryNodeResponse, CreateStoryRequest
from schemas.job import StoryJobResponse
from core.story_generator import StoryGenerator

router = APIRouter(
    prefix='/stories',
    tags=['stories']
)

# Purpose:
# Tracks users across multiple API requests
# Persists in browser via cookies
# Links stories to specific users/sessions
def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

# User sends theme → Job created → Background task queued → Immediate response
@router.post("/create", response_model=StoryJobResponse)
def create_story(request: CreateStoryRequest, background_tasks: BackgroundTasks, response: Response, session_id: str = Depends(get_session_id), db: Session = Depends(get_db)):
    """
    Initiates the story generation process based on the provided theme.
    This endpoint creates a new story job and processes it in the background.
    """
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    job_id = str(uuid.uuid4())

    job = StoryJob(
        job_id = job_id,            # Unique job identifier
        session_id = session_id,    # Link to user session
        theme = request.theme,      # User's story theme
        status = "pending"          # Initial job state
    )

    db.add(job)
    db.commit()

    background_tasks.add_task(generate_story_task, job_id, request.theme, session_id)
    return job

# Background story Generation task, AI work
# "pending" → "processing" → "completed" (success)
#                       ↓
#                    "failed" (on error)
def generate_story_task(job_id: str, theme: str, session_id: str):
    db = SessionLocal() # New DB session for background task

    try:
        job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()
        if not job:
            return
        
        try:
            job.status = "processing"
            db.commit()
            
            # story generation logic
            story = StoryGenerator.generate_story(db, session_id, theme)

            job.story_id = story.id             # Link generated story to job   
            job.status = "completed"            # Mark as successful
            job.completed_at = datetime.now()   # Record completion time
            db.commit()
        
        except Exception as e:
            job.status = "failed"
            job.completed_at = datetime.now()
            job.error = str(e)
            db.commit()

    finally:
        db.close()

# Story Retrieval Endpoint - Get Complete Story
#  Purpose: Returns the full interactive story with all paths and choices
@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)
def get_complete_story(story_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the complete story including all nodes and choices.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    complete_story = build_complete_story_tree(db, story)
    return complete_story

def build_complete_story_tree(db: Session, story: Story) -> CompleteStoryResponse:
    nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()
    node_dict = {}
    for node in nodes:
        node_response = CompleteStoryNodeResponse(
            id=node.id,
            content=node.content,
            is_ending=node.is_ending,
            is_winning_ending=node.is_winning_ending,
            is_root=node.is_root,
            options=node.options
        )
        node_dict[node.id] = node_response

    root_node = next((n for n in node_dict.values() if n.is_root), None)
    if not root_node:
        raise HTTPException(status_code=500, detail="Root node not found")
    
    return CompleteStoryResponse(
        id=story.id,
        title=story.title,
        session_id=story.session_id,
        created_at=story.created_at,
        root_node=node_dict[root_node.id],
        all_nodes=node_dict
    )

# {
#   "id": 1,
#   "title": "The Underwater Pirates",
#   "session_id": "user123",
#   "created_at": "2025-09-30T...",
#   "root_node": {
#     "id": 1,
#     "content": "You dive into the ocean...",
#     "is_root": true,
#     "options": [...]
#   },
#   "all_nodes": {
#     "1": {...},
#     "2": {...},
#     "3": {...}
#   }
# }