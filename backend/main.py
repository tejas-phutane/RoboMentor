"""
Main FastAPI application for RoboMentor.
"""

import sys
import os

# Add the current directory to Python path for standalone execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    # Try relative imports first (when run as package)
    from .api import (
        ai_router,
        quiz_router,
        learning_router,
        scheduler_router,
        recommendations_router,
        calendar_router,
        trends_router
    )
    from .models import engine
    from .models.models import Base
    from .config import config
except ImportError:
    # Fall back to absolute imports (when run as standalone executable)
    from api import (
        ai_router,
        quiz_router,
        learning_router,
        scheduler_router,
        recommendations_router,
        calendar_router,
        trends_router
    )
    from models import engine
    from models.models import Base
    from config import config

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="RoboMentor API",
    description="AI-powered learning system for robotics engineers",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_router)
app.include_router(quiz_router)
app.include_router(learning_router)
app.include_router(scheduler_router)
app.include_router(recommendations_router)
app.include_router(calendar_router)
app.include_router(trends_router)

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to RoboMentor API"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.HOST, port=config.PORT)