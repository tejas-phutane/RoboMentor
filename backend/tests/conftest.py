"""
Pytest configuration and fixtures for RoboMentor backend tests.
"""

import pytest
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_gpt_client():
    """Mock GPT client for testing."""
    mock_client = Mock()
    mock_client.chat_completion.return_value = {
        "choices": [{"message": {"content": "Mock AI response"}}]
    }
    mock_client.generate_text.return_value = "Mock generated text"
    return mock_client


@pytest.fixture
def mock_openai_key():
    """Mock OpenAI API key environment variable."""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        yield


@pytest.fixture
def sample_user_skills():
    """Sample user skills data."""
    return {
        "Python": 75.0,
        "Machine Learning": 60.0,
        "Computer Vision": 45.0,
        "Robotics": 30.0
    }


@pytest.fixture
def sample_user_goals():
    """Sample user goals data."""
    return ["Master Robotics", "Learn Computer Vision", "Build ML Projects"]


@pytest.fixture
def sample_learning_items():
    """Sample learning items for scheduler testing."""
    return [
        {
            "id": "item1",
            "title": "Learn Python Basics",
            "duration_minutes": 60,
            "priority": 8,
            "dependencies": [],
            "completed": False,
            "progress_percentage": 0.0
        },
        {
            "id": "item2",
            "title": "Machine Learning Fundamentals",
            "duration_minutes": 90,
            "priority": 9,
            "dependencies": ["item1"],
            "completed": False,
            "progress_percentage": 0.0
        }
    ]