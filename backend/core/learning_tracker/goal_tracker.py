from typing import Dict, List, Optional
import uuid
from datetime import datetime, timedelta


class GoalTracker:
    """
    Tracks learning goals and their progress.
    """

    def __init__(self):
        self.goals = {}  # In a real implementation, this would be a database

    def create_goal(self, title: str, description: str, domain: str,
                   target_skills: List[str], timeframe_weeks: int,
                   priority: str = "Medium") -> Dict:
        """
        Create a new learning goal.

        Args:
            title: Goal title
            description: Goal description
            domain: Domain (e.g., "Robotics", "CV", "RL")
            target_skills: Skills to develop
            timeframe_weeks: Timeframe in weeks
            priority: Priority level

        Returns:
            Goal dictionary
        """
        goal = {
            "goal_id": str(uuid.uuid4()),
            "title": title,
            "description": description,
            "domain": domain,
            "target_skills": target_skills,
            "timeframe_weeks": timeframe_weeks,
            "priority": priority,
            "status": "Active",
            "progress_percent": 0.0,
            "created_date": datetime.now().isoformat(),
            "expected_completion_date": (datetime.now() + timedelta(weeks=timeframe_weeks)).isoformat(),
            "milestones": self._generate_milestones(target_skills, timeframe_weeks),
            "linked_projects": [],
            "notes": []
        }

        self.goals[goal["goal_id"]] = goal
        return goal

    def _generate_milestones(self, target_skills: List[str], timeframe_weeks: int) -> List[Dict]:
        """Generate milestones for the goal."""
        milestones = []
        skills_per_milestone = max(1, len(target_skills) // 3)  # Divide into 3 milestones

        for i in range(3):
            start_idx = i * skills_per_milestone
            end_idx = min((i + 1) * skills_per_milestone, len(target_skills))
            milestone_skills = target_skills[start_idx:end_idx]

            milestone = {
                "milestone_id": str(uuid.uuid4()),
                "title": f"Milestone {i+1}: Master {', '.join(milestone_skills)}",
                "target_skills": milestone_skills,
                "target_date": (datetime.now() + timedelta(weeks=(i+1) * timeframe_weeks // 3)).isoformat(),
                "status": "Pending",
                "progress_percent": 0.0,
                "description": f"Develop proficiency in {', '.join(milestone_skills)}"
            }
            milestones.append(milestone)

        return milestones

    def update_goal_progress(self, goal_id: str, progress_percent: float,
                           notes: Optional[str] = None) -> Dict:
        """
        Update goal progress.

        Args:
            goal_id: Goal ID
            progress_percent: New progress percentage
            notes: Optional progress notes

        Returns:
            Updated goal
        """
        if goal_id not in self.goals:
            raise ValueError(f"Goal {goal_id} not found")

        goal = self.goals[goal_id]
        goal["progress_percent"] = min(progress_percent, 100.0)

        if notes:
            goal["notes"].append({
                "date": datetime.now().isoformat(),
                "note": notes
            })

        # Update milestone progress
        self._update_milestone_progress(goal)

        # Check if goal is completed
        if goal["progress_percent"] >= 100.0:
            goal["status"] = "Completed"

        return goal

    def _update_milestone_progress(self, goal: Dict):
        """Update progress for goal milestones."""
        total_milestones = len(goal["milestones"])
        if total_milestones == 0:
            return

        # Simple progress distribution across milestones
        base_progress = goal["progress_percent"] / total_milestones

        for i, milestone in enumerate(goal["milestones"]):
            # Later milestones get less progress until earlier ones are complete
            milestone_progress = base_progress * (i + 1) / total_milestones
            milestone["progress_percent"] = min(milestone_progress, 100.0)

            if milestone["progress_percent"] >= 100.0:
                milestone["status"] = "Completed"
            elif milestone["progress_percent"] > 0:
                milestone["status"] = "In Progress"

    def get_active_goals(self) -> List[Dict]:
        """Get all active goals."""
        return [goal for goal in self.goals.values() if goal["status"] == "Active"]

    def get_goal_by_id(self, goal_id: str) -> Optional[Dict]:
        """Get a specific goal by ID."""
        return self.goals.get(goal_id)

    def link_project_to_goal(self, goal_id: str, project_id: str):
        """
        Link a project to a goal.

        Args:
            goal_id: Goal ID
            project_id: Project ID
        """
        if goal_id in self.goals:
            if project_id not in self.goals[goal_id]["linked_projects"]:
                self.goals[goal_id]["linked_projects"].append(project_id)

    def calculate_goal_completion_rate(self, goal_id: str) -> Dict:
        """
        Calculate detailed completion metrics for a goal.

        Args:
            goal_id: Goal ID

        Returns:
            Completion metrics
        """
        goal = self.get_goal_by_id(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        # Calculate time-based progress
        created_date = datetime.fromisoformat(goal["created_date"])
        expected_completion = datetime.fromisoformat(goal["expected_completion_date"])
        now = datetime.now()

        total_timeframe = (expected_completion - created_date).days
        elapsed_time = (now - created_date).days
        time_progress = min(elapsed_time / total_timeframe, 1.0) * 100 if total_timeframe > 0 else 0

        # Calculate milestone completion
        milestones = goal["milestones"]
        completed_milestones = sum(1 for m in milestones if m["status"] == "Completed")
        milestone_completion = (completed_milestones / len(milestones)) * 100 if milestones else 100

        return {
            "goal_id": goal_id,
            "overall_progress": goal["progress_percent"],
            "time_progress": time_progress,
            "milestone_completion": milestone_completion,
            "is_on_track": goal["progress_percent"] >= time_progress,
            "days_remaining": max(0, (expected_completion - now).days),
            "completed_milestones": completed_milestones,
            "total_milestones": len(milestones)
        }

    def get_goals_by_domain(self, domain: str) -> List[Dict]:
        """Get goals filtered by domain."""
        return [goal for goal in self.goals.values() if goal["domain"] == domain]

    def get_overdue_goals(self) -> List[Dict]:
        """Get goals that are past their expected completion date."""
        now = datetime.now()
        overdue = []

        for goal in self.goals.values():
            if goal["status"] == "Active":
                expected_date = datetime.fromisoformat(goal["expected_completion_date"])
                if now > expected_date:
                    overdue.append(goal)

        return overdue