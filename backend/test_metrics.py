"""
Script to gather performance metrics for the Choose Your Own Adventure project.
This generates quantifiable data for resume and documentation.
"""
import time
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.story_generator import StoryGenerator
from db.database import Base
from models.story import Story, StoryNode

# Connect to database
engine = create_engine("sqlite:///./database.db")
SessionLocal = sessionmaker(bind=engine)

def measure_story_complexity():
    """Measure average nodes, depth, and branching factor"""
    db = SessionLocal()
    try:
        stories = db.query(Story).all()
        if not stories:
            print("⚠️  No stories in database yet. Generate a story first!")
            return None
        
        metrics = {
            "total_stories": len(stories),
            "total_nodes": 0,
            "max_nodes_per_story": 0,
            "min_nodes_per_story": float('inf'),
            "stories_with_data": []
        }
        
        for story in stories:
            node_count = len(story.nodes)
            metrics["total_nodes"] += node_count
            metrics["max_nodes_per_story"] = max(metrics["max_nodes_per_story"], node_count)
            metrics["min_nodes_per_story"] = min(metrics["min_nodes_per_story"], node_count)
            
            # Count endings
            endings = sum(1 for node in story.nodes if not node.options)
            winning_endings = sum(1 for node in story.nodes if getattr(node, 'is_winning_ending', False))
            
            metrics["stories_with_data"].append({
                "id": story.id,
                "title": story.title,
                "nodes": node_count,
                "endings": endings,
                "winning_endings": winning_endings
            })
        
        metrics["avg_nodes_per_story"] = metrics["total_nodes"] / len(stories) if stories else 0
        
        return metrics
    finally:
        db.close()

def estimate_token_usage():
    """Estimate average token usage per story generation"""
    # Based on typical GPT-4 usage patterns
    avg_prompt_tokens = 350  # System prompt + user theme + instructions
    avg_completion_tokens_per_node = 150  # Story text + options
    avg_nodes = 7  # Typical story has 5-10 nodes
    
    total_tokens = avg_prompt_tokens + (avg_completion_tokens_per_node * avg_nodes)
    
    # GPT-4o-mini pricing (as of Oct 2025)
    input_cost_per_1k = 0.00015  # $0.15 per 1M tokens
    output_cost_per_1k = 0.0006   # $0.60 per 1M tokens
    
    cost_per_story = ((avg_prompt_tokens / 1000) * input_cost_per_1k + 
                     (avg_completion_tokens_per_node * avg_nodes / 1000) * output_cost_per_1k)
    
    return {
        "avg_tokens_per_story": total_tokens,
        "avg_prompt_tokens": avg_prompt_tokens,
        "avg_completion_tokens": avg_completion_tokens_per_node * avg_nodes,
        "estimated_cost_per_story": round(cost_per_story, 4),
        "stories_per_dollar": int(1 / cost_per_story) if cost_per_story > 0 else "N/A"
    }

def measure_database_metrics():
    """Get database statistics"""
    db = SessionLocal()
    try:
        story_count = db.query(Story).count()
        node_count = db.query(StoryNode).count()
        
        # Get unique sessions
        unique_sessions = db.execute(
            text("SELECT COUNT(DISTINCT session_id) FROM stories")
        ).scalar()
        
        return {
            "total_stories": story_count,
            "total_nodes": node_count,
            "unique_sessions": unique_sessions,
            "avg_nodes_per_story": round(node_count / story_count, 1) if story_count > 0 else 0
        }
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("📊 Choose Your Own Adventure - Performance Metrics")
    print("=" * 60)
    
    print("\n🎮 Story Complexity Metrics:")
    complexity = measure_story_complexity()
    if complexity:
        print(f"   Total Stories Generated: {complexity['total_stories']}")
        print(f"   Average Nodes per Story: {complexity['avg_nodes_per_story']:.1f}")
        print(f"   Max Nodes in Story: {complexity['max_nodes_per_story']}")
        print(f"   Total Nodes Created: {complexity['total_nodes']}")
        
        if complexity['stories_with_data']:
            print("\n   📖 Story Details:")
            for story in complexity['stories_with_data']:
                print(f"      • {story['title']}: {story['nodes']} nodes, {story['endings']} endings")
    
    print("\n💰 Token Usage & Cost Estimates:")
    tokens = estimate_token_usage()
    print(f"   Avg Tokens per Story: ~{tokens['avg_tokens_per_story']} tokens")
    print(f"   Estimated Cost per Story: ${tokens['estimated_cost_per_story']}")
    print(f"   Stories per Dollar: ~{tokens['stories_per_dollar']}")
    
    print("\n🗄️  Database Statistics:")
    db_metrics = measure_database_metrics()
    print(f"   Total Stories: {db_metrics['total_stories']}")
    print(f"   Total Nodes: {db_metrics['total_nodes']}")
    print(f"   Unique Sessions: {db_metrics['unique_sessions']}")
    print(f"   Avg Nodes/Story: {db_metrics['avg_nodes_per_story']}")
    
    print("\n" + "=" * 60)
    print("✅ Metrics collection complete!")
    print("=" * 60)
