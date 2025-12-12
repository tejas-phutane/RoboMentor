"""
Learning Tracker API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import get_db_session
from ..core.ai_engine import GPTClient, Recommender
from ..core.learning_tracker import PathGenerator

router = APIRouter(prefix="/api", tags=["Learning Tracker"])

gpt_client = GPTClient()
recommender = Recommender(gpt_client)
path_generator = PathGenerator(recommender)

@router.get("/paths/active")
def get_active_paths(db: Session = Depends(get_db_session)):
    """Get current learning paths."""
    # Placeholder - would query database
    return {"paths": []}

@router.post("/paths/create")
def create_path(user_skills: dict, user_goals: list, hours_per_week: int = 10, db: Session = Depends(get_db_session)):
    """Create new learning path."""
    path = path_generator.generate_learning_path(user_skills, user_goals, hours_per_week)
    return {"path": path}

@router.put("/paths/{path_id}/next-phase")
def next_phase(path_id: str, db: Session = Depends(get_db_session)):
    """Move to next phase."""
    # Placeholder
    return {"result": "Phase advanced"}

@router.get("/paths/{path_id}/recommendations")
def get_recommendations(path_id: str, db: Session = Depends(get_db_session)):
    """AI-generated next steps."""
    # Placeholder
    return {"recommendations": []}

@router.get("/skills/profile")
def get_skills_profile(db: Session = Depends(get_db_session)):
    """Get user's skills snapshot."""
    # Placeholder
    return {"profile": {}}

@router.put("/skills/{skill_id}/proficiency")
def update_proficiency(skill_id: str, level: float, db: Session = Depends(get_db_session)):
    """Update skill level."""
    # Placeholder
    return {"result": "Updated"}

@router.get("/concepts/search")
def search_concepts(query: str, db: Session = Depends(get_db_session)):
    """Search concepts by keyword."""
    # Placeholder
    return {"concepts": []}

@router.post("/concepts/from-obsidian")
def sync_concepts_from_obsidian(vault_path: str, db: Session = Depends(get_db_session)):
    """Sync concepts from vault."""
    # Placeholder
    return {"result": "Synced"}

@router.get("/goals/active")
def get_active_goals(db: Session = Depends(get_db_session)):
    """Get active goals."""
    # Placeholder
    return {"goals": []}

@router.post("/goals/create")
def create_goal(title: str, description: str, domain: str, timeframe_weeks: int = 12, db: Session = Depends(get_db_session)):
    """Create new goal."""
    # Placeholder
    return {"goal": {"title": title, "description": description}}

@router.put("/goals/{goal_id}/progress")
def update_progress(goal_id: str, progress: float, db: Session = Depends(get_db_session)):
    """Update goal progress."""
    # Placeholder
    return {"result": "Updated"}