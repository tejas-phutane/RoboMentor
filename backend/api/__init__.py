"""
API routers for RoboMentor FastAPI application.
"""

from .ai_engine import router as ai_router, quiz_router
from .learning_tracker import router as learning_router
from .adaptive_scheduler import router as scheduler_router
from .upgrade_recommendations import router as recommendations_router
from .calendar_integration import router as calendar_router
from .trend_integrations import router as trends_router

__all__ = [
    'ai_router',
    'quiz_router',
    'learning_router',
    'scheduler_router',
    'recommendations_router',
    'calendar_router',
    'trends_router'
]