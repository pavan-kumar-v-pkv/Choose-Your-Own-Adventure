from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime

# How they relate and work together:
# 1. API Request: User sends CreateStoryRequest with a theme
# 2. Story Generation: Backend creates story with multiple StoryNodes
# 3. API Response: Returns CompleteStoryResponse with full story structure
# 4. Gameplay: Frontend uses StoryOptionsSchema to show choices and navigate between nodes


# Purpose: Represents a choice/option the player can make in the story
# text: str: The text of the choice (e.g., "Enter the dark cave")
# node_id: Optional[int] = None: ID of the story node this choice leads to (optional, can be set later)
# Example:
# {
#   "text": "Open the mysterious door",
#   "node_id": 5
# }
class StoryOptionsSchema(BaseModel):
    text: str
    node_id: Optional[int] = None


# Purpose: Base schema for story nodes (chapters/segments)
# content: str: The actual story text/narrative
# is_ending: bool = False: Whether this node ends the story
# is_winning_ending: bool = False: Whether this is a successful ending
# {
#   "content": "You find yourself in a dark forest...",
#   "is_ending": false,
#   "is_winning_ending": false
# }
class StoryNodeBase(BaseModel):
    content: str
    is_ending: bool = False
    is_winning_ending: bool = False


# Purpose: Full story node response with ID and options (inherits from StoryNodeBase)
# id: int: Unique identifier for the node
# options: List[StoryOptionsSchema] = []: List of choices available from this node
# Config: from_attributes = True: Allows creation from SQLAlchemy model attributes
# {
#   "id": 1,
#   "content": "You approach a haunted castle...",
#   "is_ending": false,
#   "is_winning_ending": false,
#   "options": [
#     {"text": "Enter the front door", "node_id": 2},
#     {"text": "Sneak around back", "node_id": 3}
#   ]
# }
class CompleteStoryNodeResponse(StoryNodeBase):
    id: int
    options: List[StoryOptionsSchema] = []

    class Config:
        from_attributes = True


# Purpose: Base schema for stories
# title: str: Name of the adventure story
# session_id: Optional[str] = None: Session identifier for tracking user progress
# Config: from_attributes = True: SQLAlchemy compatibility
class StoryBase(BaseModel):
    title: str
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


# Purpose: Request payload when user wants to create a new story
# theme: str: The theme/genre for story generation (e.g., "medieval fantasy", "space adventure")
# Example usage:
# {
#   "theme": "underwater adventure with pirates"
# }
class CreateStoryRequest(BaseModel):
    theme: str

    
# Purpose: Complete story response with all data (inherits from StoryBase)
# id: int: Unique story identifier
# created_at: datetime: When the story was created
# root_node: CompleteStoryNodeResponse: The starting node of the story
# all_nodes: Dict[int, CompleteStoryNodeResponse]: All story nodes mapped by their IDs
# Example:
# {
#   "id": 1,
#   "title": "The Haunted Castle",
#   "session_id": "abc123",
#   "created_at": "2025-09-29T10:30:00Z",
#   "root_node": {
#     "id": 1,
#     "content": "You approach a dark castle...",
#     "options": [...]
#   },
#   "all_nodes": {
#     "1": {...},
#     "2": {...},
#     "3": {...}
#   }
# }
class CompleteStoryResponse(StoryBase):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: Dict[int, CompleteStoryNodeResponse]

    class Config:
        from_attributes = True
