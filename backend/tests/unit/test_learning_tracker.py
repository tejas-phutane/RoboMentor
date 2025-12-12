"""
Unit tests for Learning Tracker module components.
"""

import pytest
from datetime import datetime, timedelta
from ...core.learning_tracker.goal_tracker import GoalTracker
from ...core.learning_tracker.path_generator import PathGenerator
from ...core.learning_tracker.skill_analyzer import SkillAnalyzer


class TestGoalTracker:
    """Test goal tracker functionality."""

    def test_init(self):
        """Test goal tracker initialization."""
        tracker = GoalTracker()
        assert tracker.goals == {}

    def test_create_goal(self):
        """Test goal creation."""
        tracker = GoalTracker()
        goal = tracker.create_goal(
            title="Learn Robotics",
            description="Master robotics fundamentals",
            domain="Robotics",
            target_skills=["Python", "Control Systems"],
            timeframe_weeks=8,
            priority="High"
        )

        assert goal["goal_id"] is not None
        assert goal["title"] == "Learn Robotics"
        assert goal["domain"] == "Robotics"
        assert goal["target_skills"] == ["Python", "Control Systems"]
        assert goal["timeframe_weeks"] == 8
        assert goal["priority"] == "High"
        assert goal["status"] == "Active"
        assert goal["progress_percent"] == 0.0
        assert "milestones" in goal
        assert len(goal["milestones"]) == 3  # Divided into 3 milestones

    def test_update_goal_progress(self):
        """Test goal progress update."""
        tracker = GoalTracker()
        goal = tracker.create_goal("Test Goal", "Test", "Test", ["Skill1"], 4)

        updated_goal = tracker.update_goal_progress(goal["goal_id"], 50.0, "Made good progress")

        assert updated_goal["progress_percent"] == 50.0
        assert len(updated_goal["notes"]) == 1
        assert updated_goal["notes"][0]["note"] == "Made good progress"

    def test_update_goal_progress_completion(self):
        """Test goal completion when progress reaches 100%."""
        tracker = GoalTracker()
        goal = tracker.create_goal("Test Goal", "Test", "Test", ["Skill1"], 4)

        updated_goal = tracker.update_goal_progress(goal["goal_id"], 100.0)

        assert updated_goal["status"] == "Completed"

    def test_get_active_goals(self):
        """Test getting active goals."""
        tracker = GoalTracker()
        goal1 = tracker.create_goal("Active Goal", "Test", "Test", ["Skill1"], 4)
        goal2 = tracker.create_goal("Completed Goal", "Test", "Test", ["Skill2"], 4)
        tracker.update_goal_progress(goal2["goal_id"], 100.0)

        active_goals = tracker.get_active_goals()
        assert len(active_goals) == 1
        assert active_goals[0]["goal_id"] == goal1["goal_id"]

    def test_calculate_goal_completion_rate(self):
        """Test goal completion rate calculation."""
        tracker = GoalTracker()
        goal = tracker.create_goal("Test Goal", "Test", "Test", ["Skill1"], 4)

        # Set goal creation date to 2 weeks ago
        two_weeks_ago = datetime.now() - timedelta(weeks=2)
        goal["created_date"] = two_weeks_ago.isoformat()

        metrics = tracker.calculate_goal_completion_rate(goal["goal_id"])

        assert "overall_progress" in metrics
        assert "time_progress" in metrics
        assert "milestone_completion" in metrics
        assert "is_on_track" in metrics
        assert "days_remaining" in metrics

    def test_get_overdue_goals(self):
        """Test getting overdue goals."""
        tracker = GoalTracker()
        goal = tracker.create_goal("Overdue Goal", "Test", "Test", ["Skill1"], 1)

        # Set creation date to more than a week ago
        week_ago = datetime.now() - timedelta(weeks=2)
        goal["created_date"] = week_ago.isoformat()

        overdue = tracker.get_overdue_goals()
        assert len(overdue) == 1
        assert overdue[0]["goal_id"] == goal["goal_id"]


class TestSkillAnalyzer:
    """Test skill analyzer functionality."""

    def test_init(self):
        """Test skill analyzer initialization."""
        analyzer = SkillAnalyzer()
        assert "Computer Vision" in analyzer.skill_hierarchy
        assert "Robotics" in analyzer.skill_hierarchy

    def test_analyze_skill_gaps(self, sample_user_skills):
        """Test skill gap analysis."""
        analyzer = SkillAnalyzer()
        target_skills = {"Python": 90.0, "Machine Learning": 80.0, "Robotics": 70.0}

        gaps = analyzer.analyze_skill_gaps(sample_user_skills, target_skills)

        assert "gaps" in gaps
        assert "average_gap" in gaps
        assert "total_gap_hours" in gaps
        assert "recommendations" in gaps

        # Check Python gap (75 -> 90, gap of 15)
        assert "Python" in gaps["gaps"]
        python_gap = gaps["gaps"]["Python"]
        assert python_gap["gap_size"] == 15.0
        assert python_gap["current"] == 75.0
        assert python_gap["target"] == 90.0

    def test_identify_learning_sequence(self):
        """Test learning sequence identification."""
        analyzer = SkillAnalyzer()
        skill_gaps = {
            "Robotics": {"priority": 0.8, "gap_size": 40.0},
            "Control Systems": {"priority": 0.9, "gap_size": 50.0},
            "Computer Vision": {"priority": 0.7, "gap_size": 30.0}
        }

        sequence = analyzer.identify_learning_sequence(skill_gaps)

        # Control Systems should come first (highest priority)
        assert sequence[0] == "Control Systems"
        assert len(sequence) == 3

    def test_calculate_skill_progression(self):
        """Test skill progression calculation."""
        analyzer = SkillAnalyzer()

        progression = analyzer.calculate_skill_progression(
            skill="Python",
            current_level=50.0,
            hours_invested=20
        )

        assert progression["current_level"] == 50.0
        assert progression["hours_invested"] == 20
        assert "expected_new_level" in progression
        assert "improvement" in progression
        assert "time_to_next_milestone" in progression

        # Expected improvement should be positive
        assert progression["improvement"] > 0


class TestPathGenerator:
    """Test learning path generator functionality."""

    def test_init(self, mock_gpt_client):
        """Test path generator initialization."""
        from ...core.ai_engine.recommender import Recommender
        recommender = Recommender(mock_gpt_client)
        generator = PathGenerator(recommender)
        assert generator.recommender == recommender

    def test_generate_learning_path(self, mock_gpt_client, sample_user_skills, sample_user_goals):
        """Test learning path generation."""
        from ...core.ai_engine.recommender import Recommender
        mock_gpt_client.generate_text.return_value = '''
        {
            "primary_topic": {"name": "Machine Learning", "estimated_hours": 40},
            "next_topics": [
                {"topic": "Deep Learning", "estimated_hours": 60},
                {"topic": "Computer Vision", "estimated_hours": 50}
            ]
        }
        '''

        recommender = Recommender(mock_gpt_client)
        generator = PathGenerator(recommender)

        path = generator.generate_learning_path(
            sample_user_skills,
            sample_user_goals,
            available_hours_per_week=10,
            timeframe_weeks=8
        )

        assert "path_id" in path
        assert "title" in path
        assert "phases" in path
        assert len(path["phases"]) > 0
        assert path["current_phase"] == 1
        assert path["completion_percentage"] == 0.0

    def test_generate_basic_path_fallback(self, sample_user_skills, sample_user_goals):
        """Test basic path generation when AI fails."""
        from unittest.mock import Mock
        mock_recommender = Mock()
        mock_recommender.recommend_next_topic.return_value = {"error": "API failure"}

        generator = PathGenerator(mock_recommender)

        path = generator.generate_learning_path(
            sample_user_skills,
            sample_user_goals,
            available_hours_per_week=10,
            timeframe_weeks=8
        )

        assert "path_id" in path
        assert "phases" in path
        assert len(path["phases"]) == 3  # Basic path has 3 phases

    def test_update_path_progress(self):
        """Test path progress update."""
        from unittest.mock import Mock
        mock_recommender = Mock()
        generator = PathGenerator(mock_recommender)

        path = {
            "path_id": "test-path",
            "current_phase": 1,
            "completion_percentage": 0.0,
            "phases": [
                {"phase": 1, "title": "Phase 1"},
                {"phase": 2, "title": "Phase 2"},
                {"phase": 3, "title": "Phase 3"}
            ],
            "adaptive_adjustments": []
        }

        updated_path = generator.update_path_progress(path, 1, {"Python": 80.0})

        assert updated_path["current_phase"] == 2
        assert updated_path["completion_percentage"] == 33.33  # 1/3 completed
        assert len(updated_path["adaptive_adjustments"]) == 1