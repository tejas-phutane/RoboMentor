from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta
from ..ai_engine.recommender import Recommender


class PathGenerator:
    """
    Generates personalized learning paths based on user skills and goals.
    """

    def __init__(self, recommender: Recommender):
        self.recommender = recommender

    def generate_learning_path(self, user_skills: Dict[str, float],
                             user_goals: List[str], available_hours_per_week: int = 10,
                             timeframe_weeks: int = 12) -> Dict:
        """
        Generate a personalized learning path.

        Args:
            user_skills: Dictionary of skill names to proficiency levels (0-100)
            user_goals: List of learning goals
            available_hours_per_week: Hours available for learning per week
            timeframe_weeks: Total timeframe in weeks

        Returns:
            Learning path dictionary
        """
        # Get AI recommendations for the path
        recommendations = self.recommender.recommend_next_topic(
            user_skills, user_goals, available_hours_per_week * timeframe_weeks
        )

        if "error" in recommendations:
            return self._generate_basic_path(user_skills, user_goals, available_hours_per_week, timeframe_weeks)

        # Build the learning path structure
        path = {
            "path_id": str(uuid.uuid4()),
            "title": f"Learning Path for {', '.join(user_goals[:2])}",
            "goal_id": None,  # Would be linked to actual goal in DB
            "status": "Active",
            "target_skills": list(user_skills.keys()),
            "current_phase": 1,
            "phases": self._build_phases(recommendations, timeframe_weeks, available_hours_per_week),
            "completion_percentage": 0.0,
            "deadline": (datetime.now() + timedelta(weeks=timeframe_weeks)).isoformat(),
            "created_date": datetime.now().isoformat(),
            "adaptive_adjustments": []
        }

        return path

    def _generate_basic_path(self, user_skills: Dict[str, float], user_goals: List[str],
                           available_hours_per_week: int, timeframe_weeks: int) -> Dict:
        """Generate a basic learning path when AI recommendations fail."""
        # Find the weakest skills
        weakest_skills = sorted(user_skills.items(), key=lambda x: x[1])[:3]

        phases = []
        total_hours = available_hours_per_week * timeframe_weeks
        hours_per_phase = total_hours // 3

        for i, (skill, level) in enumerate(weakest_skills, 1):
            phase = {
                "phase": i,
                "title": f"Improve {skill} Fundamentals",
                "concepts": [f"Core {skill} concepts"],
                "duration_estimate_hours": hours_per_phase,
                "resources": [f"Online tutorials for {skill}"],
                "milestone_criteria": f"Achieve 70% proficiency in {skill}",
                "estimated_completion": (datetime.now() + timedelta(weeks=i*4)).isoformat()
            }
            phases.append(phase)

        return {
            "path_id": str(uuid.uuid4()),
            "title": f"Basic Learning Path for {', '.join(user_goals[:2])}",
            "status": "Active",
            "target_skills": list(user_skills.keys()),
            "current_phase": 1,
            "phases": phases,
            "completion_percentage": 0.0,
            "deadline": (datetime.now() + timedelta(weeks=timeframe_weeks)).isoformat(),
            "created_date": datetime.now().isoformat(),
            "adaptive_adjustments": []
        }

    def _build_phases(self, recommendations: Dict, total_weeks: int, hours_per_week: int) -> List[Dict]:
        """Build learning path phases from AI recommendations."""
        phases = []
        total_hours = total_weeks * hours_per_week

        # Extract topics from recommendations
        next_topics = recommendations.get('next_topics', [])
        primary_topic = recommendations.get('primary_topic', {})

        if primary_topic:
            # Add primary topic as first phase
            phase1 = {
                "phase": 1,
                "title": f"Phase 1: {primary_topic.get('name', 'Primary Topic')}",
                "concepts": [primary_topic.get('name', 'Topic')],
                "duration_estimate_hours": primary_topic.get('estimated_hours', total_hours // 3),
                "resources": primary_topic.get('resources', []),
                "milestone_criteria": f"Complete {primary_topic.get('name', 'topic')} assessment",
                "estimated_completion": (datetime.now() + timedelta(weeks=total_weeks//3)).isoformat()
            }
            phases.append(phase1)

        # Add additional phases from next_topics
        remaining_topics = next_topics[:2]  # Limit to 2 additional phases
        hours_remaining = total_hours - (phases[0]['duration_estimate_hours'] if phases else 0)
        hours_per_remaining_phase = hours_remaining // len(remaining_topics) if remaining_topics else 0

        for i, topic in enumerate(remaining_topics, 2):
            phase = {
                "phase": i,
                "title": f"Phase {i}: {topic.get('topic', 'Topic')}",
                "concepts": [topic.get('topic', 'Topic')],
                "duration_estimate_hours": topic.get('estimated_hours', hours_per_remaining_phase),
                "resources": topic.get('resources', []),
                "milestone_criteria": f"Master {topic.get('topic', 'topic')} concepts",
                "estimated_completion": (datetime.now() + timedelta(weeks=(i-1)*total_weeks//3)).isoformat()
            }
            phases.append(phase)

        return phases

    def update_path_progress(self, path: Dict, completed_phase: int, new_skills: Dict[str, float]) -> Dict:
        """
        Update learning path progress.

        Args:
            path: Current learning path
            completed_phase: Phase that was completed
            new_skills: Updated skill levels

        Returns:
            Updated path
        """
        path['current_phase'] = min(completed_phase + 1, len(path['phases']))
        path['completion_percentage'] = (completed_phase / len(path['phases'])) * 100

        # Add adaptive adjustment note
        adjustment = f"Phase {completed_phase} completed. Moving to phase {path['current_phase']}."
        path['adaptive_adjustments'].append(adjustment)

        return path