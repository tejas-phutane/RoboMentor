"""
Adaptive Scheduler API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import get_db_session

router = APIRouter(prefix="/api/calendar", tags=["Adaptive Scheduler"])

@router.post("/sync")
def sync_calendar(db: Session = Depends(get_db_session)):
    """Sync with calendar."""
    return {"result": "Synced"}

@router.post("/schedule-session")
def schedule_session(session_data: dict, db: Session = Depends(get_db_session)):
    """Schedule learning session."""
    return {"result": "Scheduled"}