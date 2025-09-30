# This file is the core AI component that generates interactive stories using LangChain and OpenAI. It converts user themes into complete branching narratives.
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.output_parsers import PydanticOutputParser

from core.prompts import STORY_PROMPT
from models.story import Story, StoryNode
from core.models import StoryLLMResponse, StoryNodeLLM # AI response schemas

load_dotenv()  # Load environment variables from .env file

# Call chain
# User submits theme → routers/story.py → Background task → StoryGenerator.generate_story() → Database

# Data flow
# Theme → AI Prompt → OpenAI Response → Structured Data → Database Records → API Response

# Story Table:
# ├── id: 1
# ├── title: "The Space Pirate's Quest"
# └── session_id: "user123"

# Story_Nodes Table:
# ├── Node 1 (root): "You're a space pirate captain..."
# ├── Node 2: "You attack the merchant ship..."
# ├── Node 3: "You explore the asteroid..."
# ├── Node 4 (ending): "You find treasure!"
# └── Node 5 (ending): "You get captured!"
class StoryGenerator:

    @classmethod
    def _get_llm(cls):
        return ChatOpenAI(
            model_name="gpt-4o-mini",
            temperature=0.7,
        )
    
    # Integration point:
    # Called from: story.py background task
    # Input: Database session, user session, story theme
    # Output: Complete Story object with all nodes saved to database
    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: "fantasy") -> Story:
        llm = cls._get_llm()
        # AI Prompt Engineering
        story_parser = PydanticOutputParser(pydantic_object=StoryLLMResponse)
        prompt = ChatPromptTemplate.from_messages([
            ("system", STORY_PROMPT),
            ("human", f"Create a story with the theme: {theme}"),
        ]).partial(format_instructions=story_parser.get_format_instructions())

        # AI Communication: Prompt → OpenAI API → Raw Response → Text Extraction → Structured Data
        raw_response = llm.invoke(prompt.invoke({}))

        response_text = raw_response
        if hasattr(raw_response, 'content'):
            response_text = raw_response.content

        story_structure = story_parser.parse(response_text) # Convert JSON to Python objects

        # Database Story Creation
        story_db = Story(title=story_structure.title, session_id=session_id)
        db.add(story_db)
        db.flush()  # To get the story ID

        # Root Node Processing Setup
        root_node_data = story_structure.rootNode

        if isinstance(root_node_data, dict):
            root_node_data = StoryNodeLLM(**root_node_data)

        cls._process_story_node(db, story_db.id, root_node_data, is_root=True)

        db.commit()
        return story_db
    
    #  Node Processing Engine
    # Converts AI-generated node data into database records
    @classmethod
    def _process_story_node(cls, db: Session, story_id: int, node_data: StoryNodeLLM, is_root: bool = False) -> StoryNode:
        node = StoryNode(
            story_id=story_id,
            content=node_data.content if hasattr(node_data, "content") else node_data["content"],
            is_root=is_root,
            is_ending=node_data.isEnding if hasattr(node_data, "isEnding") else node_data["isEnding"],
            is_winning_ending=node_data.isWinningEnding if hasattr(node_data, "isWinningEnding") else node_data["isWinningEnding"],
            options=[]
        )
        db.add(node)
        db.flush()  # To get node ID

        if not node.is_ending and (hasattr(node_data, "options") and node_data.options):
            options_list = []
            for option_data in node_data.options:
                next_node = option_data.nextNode
                if isinstance(next_node, dict):
                    next_node = StoryNodeLLM(**next_node)

                child_node = cls._process_story_node(db, story_id, next_node, is_root=False)

                options_list.append({
                    "text": option_data.text,
                    "node_id": child_node.id
                })

            node.options = options_list

        db.flush()  # To save options
        return node
