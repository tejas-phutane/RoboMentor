"""
Integration tests for API endpoints.
"""

import pytest
from unittest.mock import Mock, patch


class TestAIEngineAPI:
    """Test AI Engine API endpoints."""

    def test_send_message(self, client, mock_gpt_client):
        """Test sending message to AI mentor."""
        with patch('robomentor_app.backend.api.ai_engine.chat_handler') as mock_chat:
            mock_instance = Mock()
            mock_instance.send_message.return_value = "AI response"
            mock_chat.ChatHandler.return_value = mock_instance

            response = client.post("/api/chat/message", json={"message": "Hello"})

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert data["response"] == "AI response"

    def test_generate_quiz(self, client, mock_gpt_client):
        """Test quiz generation endpoint."""
        with patch('robomentor_app.backend.api.ai_engine.quiz_generator') as mock_quiz:
            mock_instance = Mock()
            mock_instance.generate_quiz.return_value = {"title": "Test Quiz", "questions": []}
            mock_quiz.QuizGenerator.return_value = mock_instance

            response = client.post("/api/quiz/generate", json={"topic": "Python"})

            assert response.status_code == 200
            data = response.json()
            assert "quiz" in data
            assert data["quiz"]["title"] == "Test Quiz"

    def test_submit_quiz(self, client):
        """Test quiz submission endpoint."""
        quiz_data = {
            "questions": [
                {"correct_answer": "A", "explanation": "Test explanation"}
            ]
        }
        user_answers = {"answers": ["A"]}

        response = client.post("/api/quiz/submit",
                             json={"quiz_data": quiz_data, "user_answers": user_answers})

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["correct"] is True


class TestLearningTrackerAPI:
    """Test Learning Tracker API endpoints."""

    def test_create_path(self, client, mock_gpt_client, sample_user_skills, sample_user_goals):
        """Test learning path creation."""
        with patch('robomentor_app.backend.api.learning_tracker.path_generator') as mock_path:
            mock_instance = Mock()
            mock_instance.generate_learning_path.return_value = {
                "path_id": "test-path",
                "title": "Test Path",
                "phases": []
            }
            mock_path.PathGenerator.return_value = mock_instance

            request_data = {
                "user_skills": sample_user_skills,
                "user_goals": sample_user_goals,
                "hours_per_week": 10
            }

            response = client.post("/api/paths/create", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert "path" in data
            assert data["path"]["path_id"] == "test-path"

    def test_create_goal(self, client):
        """Test goal creation endpoint."""
        goal_data = {
            "title": "Learn Robotics",
            "description": "Master robotics fundamentals",
            "domain": "Robotics",
            "timeframe_weeks": 8
        }

        response = client.post("/api/goals/create", json=goal_data)

        assert response.status_code == 200
        data = response.json()
        assert "goal" in data
        assert data["goal"]["title"] == "Learn Robotics"


class TestAdaptiveSchedulerAPI:
    """Test Adaptive Scheduler API endpoints."""

    def test_sync_calendar(self, client):
        """Test calendar synchronization."""
        response = client.post("/api/calendar/sync")

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Synced"

    def test_schedule_session(self, client):
        """Test session scheduling."""
        session_data = {
            "title": "Learning Session",
            "duration": 60,
            "priority": 5
        }

        response = client.post("/api/calendar/schedule-session", json=session_data)

        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "Scheduled"


class TestUpgradeRecommendationsAPI:
    """Test Upgrade Recommendations API endpoints."""

    def test_get_dashboard(self, client):
        """Test dashboard data retrieval."""
        response = client.get("/api/metrics/dashboard")

        assert response.status_code == 200
        data = response.json()
        assert "dashboard" in data

    def test_get_gap_analysis(self, client):
        """Test gap analysis retrieval."""
        response = client.get("/api/metrics/gap-analysis")

        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data

    def test_get_learning_velocity(self, client):
        """Test learning velocity data retrieval."""
        response = client.get("/api/metrics/learning-velocity")

        assert response.status_code == 200
        data = response.json()
        assert "velocity" in data


class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test application health check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "RoboMentor" in data["message"]


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_invalid_request_data(self, client):
        """Test handling of invalid request data."""
        # Test with missing required fields
        response = client.post("/api/quiz/generate", json={})

        # Should handle gracefully (may return error or default response)
        assert response.status_code in [200, 400, 422]

    def test_unsupported_http_methods(self, client):
        """Test unsupported HTTP methods."""
        response = client.put("/api/chat/message", json={"message": "test"})

        # Should return 405 Method Not Allowed
        assert response.status_code == 405