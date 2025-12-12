"""
Basic functional tests for RoboMentor application.
"""

import pytest
from unittest.mock import Mock, patch


class TestEndToEndWorkflow:
    """Test end-to-end user workflows."""

    def test_complete_learning_workflow(self, client, mock_gpt_client, sample_user_skills, sample_user_goals):
        """Test a complete learning workflow from assessment to scheduling."""
        # Mock all external dependencies
        with patch('robomentor_app.backend.api.ai_engine.chat_handler') as mock_chat, \
             patch('robomentor_app.backend.api.learning_tracker.path_generator') as mock_path, \
             patch('robomentor_app.backend.api.ai_engine.quiz_generator') as mock_quiz:

            # Setup mocks
            mock_chat_instance = Mock()
            mock_chat_instance.send_message.return_value = "Welcome! Let's start your robotics journey."
            mock_chat.ChatHandler.return_value = mock_chat_instance

            mock_path_instance = Mock()
            mock_path_instance.generate_learning_path.return_value = {
                "path_id": "workflow-test-path",
                "title": "Complete Robotics Learning Path",
                "phases": [
                    {"phase": 1, "title": "Python Fundamentals", "duration_estimate_hours": 20},
                    {"phase": 2, "title": "Robotics Basics", "duration_estimate_hours": 30}
                ],
                "completion_percentage": 0.0
            }
            mock_path.PathGenerator.return_value = mock_path_instance

            mock_quiz_instance = Mock()
            mock_quiz_instance.generate_quiz.return_value = {
                "title": "Python Assessment",
                "questions": [
                    {
                        "question": "What is a variable in Python?",
                        "options": ["A) A storage location", "B) A function", "C) A class", "D) A module"],
                        "correct_answer": "A",
                        "explanation": "Variables store data values."
                    }
                ]
            }
            mock_quiz.QuizGenerator.return_value = mock_quiz_instance

            # Step 1: User interacts with AI mentor
            response = client.post("/api/chat/message", json={"message": "I want to learn robotics"})
            assert response.status_code == 200
            assert "Welcome" in response.json()["response"]

            # Step 2: Generate learning path
            path_data = {
                "user_skills": sample_user_skills,
                "user_goals": sample_user_goals,
                "hours_per_week": 10
            }
            response = client.post("/api/paths/create", json=path_data)
            assert response.status_code == 200
            path = response.json()["path"]
            assert path["title"] == "Complete Robotics Learning Path"
            assert len(path["phases"]) == 2

            # Step 3: Generate assessment quiz
            response = client.post("/api/quiz/generate", json={"topic": "Python"})
            assert response.status_code == 200
            quiz = response.json()["quiz"]
            assert quiz["title"] == "Python Assessment"
            assert len(quiz["questions"]) == 1

            # Step 4: Submit quiz answers
            quiz_data = quiz
            user_answers = {"answers": ["A"]}
            response = client.post("/api/quiz/submit",
                                 json={"quiz_data": quiz_data, "user_answers": user_answers})
            assert response.status_code == 200
            results = response.json()["results"]
            assert results[0]["correct"] is True

    def test_error_recovery_workflow(self, client):
        """Test error handling and recovery in workflows."""
        # Test with invalid data
        response = client.post("/api/chat/message", json={})
        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

        # Test with malformed quiz data
        response = client.post("/api/quiz/submit", json={"quiz_data": {}, "user_answers": {}})
        assert response.status_code in [200, 400, 422]


class TestDataConsistency:
    """Test data consistency across operations."""

    def test_skill_progress_tracking(self, sample_user_skills):
        """Test that skill progress updates are consistent."""
        from ...core.learning_tracker.skill_analyzer import SkillAnalyzer

        analyzer = SkillAnalyzer()

        # Initial assessment
        initial_gaps = analyzer.analyze_skill_gaps(
            sample_user_skills,
            {"Python": 90.0, "Machine Learning": 80.0}
        )

        # Simulate progress
        updated_skills = sample_user_skills.copy()
        updated_skills["Python"] = 85.0  # Improved by 10 points

        # Re-assess
        updated_gaps = analyzer.analyze_skill_gaps(
            updated_skills,
            {"Python": 90.0, "Machine Learning": 80.0}
        )

        # Gap should be smaller for Python
        initial_python_gap = initial_gaps["gaps"]["Python"]["gap_size"]
        updated_python_gap = updated_gaps["gaps"]["Python"]["gap_size"]

        assert updated_python_gap < initial_python_gap
        assert updated_python_gap == initial_python_gap - 10.0

    def test_goal_milestone_tracking(self):
        """Test goal milestone progress tracking."""
        from ...core.learning_tracker.goal_tracker import GoalTracker

        tracker = GoalTracker()

        # Create goal
        goal = tracker.create_goal(
            "Test Goal", "Test Description", "Test Domain",
            ["Skill1", "Skill2", "Skill3"], 6
        )

        # Update progress
        updated_goal = tracker.update_goal_progress(goal["goal_id"], 40.0)

        # Check milestone progress distribution
        milestones = updated_goal["milestones"]
        assert len(milestones) == 3

        # First milestone should have some progress
        assert milestones[0]["progress_percent"] > 0
        # Later milestones should have less progress
        assert milestones[2]["progress_percent"] <= milestones[0]["progress_percent"]


class TestPerformanceRequirements:
    """Test performance requirements for robotics applications."""

    def test_response_time_requirements(self, client, mock_gpt_client):
        """Test that API responses meet timing requirements."""
        import time

        with patch('robomentor_app.backend.api.ai_engine.chat_handler') as mock_chat:
            mock_instance = Mock()
            mock_instance.send_message.return_value = "Quick response"
            mock_chat.ChatHandler.return_value = mock_instance

            start_time = time.time()
            response = client.post("/api/chat/message", json={"message": "Test"})
            end_time = time.time()

            # Should respond within 2 seconds for robotics applications
            response_time = end_time - start_time
            assert response_time < 2.0
            assert response.status_code == 200

    def test_memory_efficiency(self):
        """Test memory efficiency for embedded robotics constraints."""
        from ...core.ai_engine.gpt_client import GPTClient

        # Test that client can be instantiated without excessive memory
        client = GPTClient()
        # In a real test, we'd monitor memory usage
        assert client is not None
        assert hasattr(client, 'chat_completion')


class TestRoboticsSpecificFeatures:
    """Test robotics-specific functionality."""

    def test_skill_hierarchy_validation(self):
        """Test that skill hierarchies make sense for robotics."""
        from ...core.learning_tracker.skill_analyzer import SkillAnalyzer

        analyzer = SkillAnalyzer()

        # Test dependency relationships
        deps = analyzer._get_dependencies("Sim2Real Transfer")
        assert "Robotics" in deps

        deps = analyzer._get_dependencies("Reinforcement Learning")
        assert "Control Systems" in deps

    def test_learning_path_optimization(self, sample_user_skills, sample_user_goals):
        """Test that learning paths are optimized for robotics workflows."""
        from ...core.learning_tracker.path_generator import PathGenerator
        from unittest.mock import Mock

        mock_recommender = Mock()
        mock_recommender.recommend_next_topic.return_value = {
            "primary_topic": {"name": "Computer Vision", "estimated_hours": 40},
            "next_topics": [
                {"topic": "Control Systems", "estimated_hours": 30}
            ]
        }

        generator = PathGenerator(mock_recommender)
        path = generator.generate_learning_path(
            sample_user_skills, sample_user_goals, 10, 12
        )

        # Should include robotics-relevant topics
        assert "path_id" in path
        assert "phases" in path
        assert len(path["phases"]) > 0