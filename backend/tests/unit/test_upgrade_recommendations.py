"""
Unit tests for Upgrade Recommendations module components.
"""

import pytest
from unittest.mock import Mock, patch
from ...core.upgrade_recommendations.recommendations_engine import UpgradeRecommendationsEngine


class TestUpgradeRecommendationsEngine:
    """Test upgrade recommendations engine."""

    def test_init(self):
        """Test engine initialization."""
        engine = UpgradeRecommendationsEngine()
        assert engine.skill_analyzer is not None
        assert engine.arxiv_trends is not None
        assert engine.github_trends is not None

    @patch('robomentor_app.backend.core.upgrade_recommendations.recommendations_engine.ArXivTrendsIntegration')
    @patch('robomentor_app.backend.core.upgrade_recommendations.recommendations_engine.GitHubTrendsIntegration')
    def test_generate_upgrade_recommendations(self, mock_github, mock_arxiv, sample_user_skills):
        """Test upgrade recommendations generation."""
        # Mock trend integrations
        mock_arxiv_instance = Mock()
        mock_arxiv_instance.get_recent_papers.return_value = [
            {"title": "Deep Learning Paper", "abstract": "About deep learning", "url": "http://example.com"}
        ]
        mock_arxiv_instance.get_trending_topics.return_value = {"deep learning": 5, "robotics": 3}
        mock_arxiv_instance.get_skill_recommendations.return_value = ["Focus on Deep Learning - trending on arXiv"]

        mock_github_instance = Mock()
        mock_github_instance.get_trending_repos.return_value = [
            {"name": "robotics-repo", "description": "Robotics project", "url": "http://github.com", "stars": 100, "topics": ["robotics"]}
        ]
        mock_github_instance.get_trending_topics.return_value = {"robotics": 8, "computer vision": 4}
        mock_github_instance.get_skill_recommendations.return_value = ["Explore Robotics - trending on GitHub"]

        mock_arxiv.return_value = mock_arxiv_instance
        mock_github.return_value = mock_github_instance

        engine = UpgradeRecommendationsEngine()
        target_skills = {"Python": 90.0, "Machine Learning": 80.0, "Robotics": 70.0}

        recommendations = engine.generate_upgrade_recommendations(
            sample_user_skills,
            target_skills,
            days_back=7
        )

        assert "skill_gaps" in recommendations
        assert "trends" in recommendations
        assert "upgrade_suggestions" in recommendations
        assert "trend_recommendations" in recommendations
        assert "learning_path" in recommendations

        # Verify API calls
        mock_arxiv_instance.get_recent_papers.assert_called_once_with(days_back=7, max_results=100)
        mock_github_instance.get_trending_repos.assert_called_once_with(days_back=7, max_results=50)

    def test_combine_trend_recommendations(self):
        """Test combining trend recommendations."""
        engine = UpgradeRecommendationsEngine()

        arxiv_recs = ["Focus on Robotics - trending on arXiv"]
        github_recs = ["Explore Computer Vision - trending on GitHub"]

        combined = engine._combine_trend_recommendations(
            {"robotics": 5},
            {"computer vision": 3}
        )

        assert isinstance(combined, list)
        assert len(combined) <= 5  # Limited to 5 recommendations

    def test_generate_upgrade_suggestions(self, sample_user_skills):
        """Test upgrade suggestions generation."""
        engine = UpgradeRecommendationsEngine()

        skill_gaps = {
            "gaps": {
                "Python": {"current": 75.0, "target": 90.0, "gap_size": 15.0, "priority": 0.6},
                "Robotics": {"current": 30.0, "target": 70.0, "gap_size": 40.0, "priority": 0.8}
            }
        }

        arxiv_topics = {"robotics": 5}
        github_topics = {"python": 3}
        arxiv_papers = [{"title": "Robotics Paper", "abstract": "About robotics", "url": "http://example.com"}]
        github_repos = [{"name": "python-repo", "description": "Python project", "url": "http://github.com", "stars": 50, "topics": ["python"]}]

        suggestions = engine._generate_upgrade_suggestions(
            skill_gaps, arxiv_topics, github_topics, arxiv_papers, github_repos
        )

        assert len(suggestions) == 2  # One for each skill gap
        assert all("skill" in s for s in suggestions)
        assert all("current_level" in s for s in suggestions)
        assert all("gap_size" in s for s in suggestions)
        assert all("priority" in s for s in suggestions)

        # Check Robotics suggestion has trending score
        robotics_suggestion = next(s for s in suggestions if s["skill"] == "Robotics")
        assert robotics_suggestion["trending_score"] == 5
        assert "arXiv" in robotics_suggestion["trend_sources"]

    def test_calculate_upgrade_priority(self):
        """Test upgrade priority calculation."""
        engine = UpgradeRecommendationsEngine()

        # High priority: large gap, low current level, trending
        priority1 = engine._calculate_upgrade_priority(50.0, 20.0, 10)
        # Lower priority: small gap, high current level, not trending
        priority2 = engine._calculate_upgrade_priority(10.0, 80.0, 0)

        assert priority1 > priority2
        assert 0 <= priority1 <= 1
        assert 0 <= priority2 <= 1

    def test_generate_reason(self):
        """Test reason generation for suggestions."""
        engine = UpgradeRecommendationsEngine()

        # Large gap
        reason1 = engine._generate_reason("Python", 60.0, 0, [])
        assert "significant skill gap" in reason1

        # Trending topic
        reason2 = engine._generate_reason("Robotics", 20.0, 5, ["arXiv"])
        assert "trending on arXiv" in reason2

        # Small gap, not trending
        reason3 = engine._generate_reason("ML", 5.0, 0, [])
        assert "fundamental robotics skill" in reason3

    def test_find_relevant_resources(self):
        """Test finding relevant resources."""
        engine = UpgradeRecommendationsEngine()

        arxiv_papers = [
            {"title": "Deep Learning Advances", "abstract": "About deep learning and neural networks", "url": "http://arxiv.org/1"},
            {"title": "Robotics Control", "abstract": "About robot control systems", "url": "http://arxiv.org/2"}
        ]

        github_repos = [
            {"name": "pytorch-examples", "description": "PyTorch deep learning examples", "url": "http://github.com/1", "stars": 1000, "topics": ["deep-learning", "pytorch"]},
            {"name": "robotics-sim", "description": "Robotics simulation toolkit", "url": "http://github.com/2", "stars": 500, "topics": ["robotics", "simulation"]}
        ]

        resources = engine._find_relevant_resources("Deep Learning", arxiv_papers, github_repos)

        assert "papers" in resources
        assert "repositories" in resources
        assert len(resources["papers"]) > 0
        assert len(resources["repositories"]) > 0

        # Should find relevant papers
        assert len(resources["papers"]) > 0

    def test_prioritize_suggestions(self):
        """Test suggestions prioritization."""
        engine = UpgradeRecommendationsEngine()

        suggestions = [
            {"skill": "Python", "priority": 0.5, "gap_size": 20.0},
            {"skill": "Robotics", "priority": 0.8, "gap_size": 40.0},
            {"skill": "ML", "priority": 0.3, "gap_size": 10.0}
        ]

        skill_gaps = {"gaps": {}}  # Mock skill gaps
        prioritized = engine._prioritize_suggestions(suggestions, skill_gaps)

        # Robotics should be first (highest priority)
        assert prioritized[0]["skill"] == "Robotics"
        # Python second
        assert prioritized[1]["skill"] == "Python"
        # ML last
        assert prioritized[2]["skill"] == "ML"

    def test_create_learning_path(self, sample_user_skills):
        """Test learning path creation."""
        engine = UpgradeRecommendationsEngine()

        suggestions = [
            {"skill": "Python", "current_level": 75.0, "gap_size": 15.0, "resources": {"papers": [], "repositories": []}},
            {"skill": "Robotics", "current_level": 30.0, "gap_size": 40.0, "resources": {"papers": [], "repositories": []}}
        ]

        skill_gaps = {
            "gaps": {
                "Python": {"priority": 0.6},
                "Robotics": {"priority": 0.8}
            }
        }

        learning_path = engine._create_learning_path(suggestions, skill_gaps)

        assert isinstance(learning_path, list)
        assert len(learning_path) == 2
        assert all("skill" in step for step in learning_path)
        assert all("estimated_hours" in step for step in learning_path)
        assert all("prerequisites" in step for step in learning_path)
        assert all("resources" in step for step in learning_path)

    @patch('robomentor_app.backend.core.upgrade_recommendations.recommendations_engine.ArXivTrendsIntegration')
    @patch('robomentor_app.backend.core.upgrade_recommendations.recommendations_engine.GitHubTrendsIntegration')
    def test_error_handling(self, mock_github, mock_arxiv):
        """Test error handling in recommendations generation."""
        # Mock integrations to raise exceptions
        mock_arxiv_instance = Mock()
        mock_arxiv_instance.get_recent_papers.side_effect = Exception("API Error")
        mock_arxiv.return_value = mock_arxiv_instance

        mock_github_instance = Mock()
        mock_github_instance.get_trending_repos.side_effect = Exception("API Error")
        mock_github.return_value = mock_github_instance

        engine = UpgradeRecommendationsEngine()

        result = engine.generate_upgrade_recommendations(
            {"Python": 50.0},
            {"Python": 80.0},
            days_back=7
        )

        assert "error" in result
        assert "API Error" in result["error"]