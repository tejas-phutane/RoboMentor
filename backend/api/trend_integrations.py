"""
Trend Integrations API endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models import get_db_session

router = APIRouter(prefix="/api/trends", tags=["Trend Integrations"])

@router.get("/arxiv")
def get_arxiv_trends(db: Session = Depends(get_db_session)):
    """Get arXiv trends."""
    return {"trends": []}

@router.get("/github")
def get_github_trends(db: Session = Depends(get_db_session)):
    """Get GitHub trends."""
    return {"trends": []}