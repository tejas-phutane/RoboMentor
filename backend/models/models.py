"""
SQLAlchemy models for RoboMentor database.
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

Base = declarative_base()

# Database URL - can be configured
from ..config import config
DATABASE_URL = config.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Get database session."""
    return SessionLocal()

class Skill(Base):
    __tablename__ = "skills"

    skill_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String)
    parent_skill_id = Column(String, ForeignKey('skills.skill_id'))
    proficiency_level = Column(Float, default=0.0)
    last_assessed = Column(DateTime)
    assessment_method = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    parent = relationship("Skill", remote_side=[skill_id])
    sub_skills = relationship("Skill")

class Concept(Base):
    __tablename__ = "concepts"

    concept_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    domain = Column(String)
    difficulty = Column(String)
    mastery_level = Column(Float, default=0.0)
    obsidian_file_path = Column(String)
    date_first_encountered = Column(DateTime)
    date_last_reviewed = Column(DateTime)
    created_date = Column(DateTime, default=datetime.utcnow)

class LearningSession(Base):
    __tablename__ = "learning_sessions"

    session_id = Column(String, primary_key=True)
    date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    type = Column(String)  # "Reading", "Tutorial", "Project", etc.
    intensity = Column(String)  # "Light", "Medium", "Deep"
    engagement_score = Column(Integer)
    reflection = Column(Text)
    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    skills = relationship("Skill", secondary="session_skills", backref="sessions")

class SessionSkill(Base):
    __tablename__ = "session_skills"

    session_id = Column(String, ForeignKey('learning_sessions.session_id'), primary_key=True)
    skill_id = Column(String, ForeignKey('skills.skill_id'), primary_key=True)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    quiz_id = Column(String, primary_key=True)
    attempt_id = Column(String, nullable=False)
    concept_id = Column(String, ForeignKey('concepts.concept_id'))
    skill_id = Column(String, ForeignKey('skills.skill_id'))
    score = Column(Float)
    time_spent_minutes = Column(Integer)
    date_attempted = Column(DateTime)
    retention_predicted = Column(Float)
    next_review_date = Column(DateTime)

    # Relationships
    concept = relationship("Concept")
    skill = relationship("Skill")

class LearningPath(Base):
    __tablename__ = "learning_paths"

    path_id = Column(String, primary_key=True)
    goal_id = Column(String, ForeignKey('goals.goal_id'))
    title = Column(String, nullable=False)
    status = Column(String)
    current_phase = Column(Integer)
    completion_percentage = Column(Float)
    deadline = Column(DateTime)
    created_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    goal = relationship("Goal")

class Goal(Base):
    __tablename__ = "goals"

    goal_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    domain = Column(String)
    timeframe_weeks = Column(Integer)
    priority = Column(String)
    status = Column(String)
    progress_percent = Column(Float, default=0.0)
    created_date = Column(DateTime, default=datetime.utcnow)
    expected_completion_date = Column(DateTime)

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    domain = Column(String)
    status = Column(String)
    repo_url = Column(String)
    created_date = Column(DateTime, default=datetime.utcnow)

class GapAnalysis(Base):
    __tablename__ = "gap_analysis"

    analysis_id = Column(String, primary_key=True)
    date_generated = Column(DateTime, default=datetime.utcnow)
    current_profile = Column(JSON)  # JSON serialized skill profile
    target_profile = Column(JSON)
    gaps_identified = Column(JSON)  # Detailed gap objects
    recommendations = Column(Text)

# Indices for performance
Index('idx_skill_domain', Skill.domain)
Index('idx_session_date', LearningSession.date)
Index('idx_quiz_date', QuizAttempt.date_attempted)
Index('idx_concept_mastery', Concept.mastery_level)
Index('idx_goal_status', Goal.status)

# Create tables
Base.metadata.create_all(bind=engine)