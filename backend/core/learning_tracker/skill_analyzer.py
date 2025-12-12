from typing import Dict, List, Tuple
import math


class SkillAnalyzer:
    """
    Analyzes user skills and identifies gaps for learning path generation.
    """

    def __init__(self):
        # Define skill hierarchy and relationships
        self.skill_hierarchy = {
            "Computer Vision": ["Object Detection", "Image Processing", "3D Vision"],
            "Robotics": ["Motion Planning", "Control Systems", "Sim2Real Transfer"],
            "Reinforcement Learning": ["Policy Gradient", "Actor-Critic", "Multi-Agent Systems"],
            "Control Systems": ["PID Control", "State Space", "Optimal Control"],
            "Sim2Real Transfer": ["Domain Randomization", "Physics Simulation", "System Identification"]
        }

    def analyze_skill_gaps(self, current_skills: Dict[str, float],
                          target_skills: Dict[str, float]) -> Dict:
        """
        Analyze gaps between current and target skill levels.

        Args:
            current_skills: Current proficiency levels (0-100)
            target_skills: Target proficiency levels (0-100)

        Returns:
            Gap analysis dictionary
        """
        gaps = {}
        total_gap = 0
        gap_count = 0

        for skill, target_level in target_skills.items():
            current_level = current_skills.get(skill, 0)
            gap_size = target_level - current_level

            if gap_size > 0:
                gaps[skill] = {
                    "current": current_level,
                    "target": target_level,
                    "gap_size": gap_size,
                    "priority": self._calculate_priority(skill, gap_size, current_skills)
                }
                total_gap += gap_size
                gap_count += 1

        # Sort gaps by priority
        sorted_gaps = sorted(gaps.items(), key=lambda x: x[1]['priority'], reverse=True)

        return {
            "gaps": dict(sorted_gaps),
            "average_gap": total_gap / gap_count if gap_count > 0 else 0,
            "total_gap_hours": self._estimate_gap_hours(total_gap),
            "recommendations": self._generate_recommendations(sorted_gaps[:3])  # Top 3 gaps
        }

    def _calculate_priority(self, skill: str, gap_size: float, current_skills: Dict[str, float]) -> float:
        """
        Calculate priority score for a skill gap.

        Priority factors:
        - Gap size (larger gaps = higher priority)
        - Current level (lower current levels = higher priority for fundamentals)
        - Dependencies (skills that others depend on = higher priority)
        """
        base_priority = gap_size / 100  # Normalize gap size

        # Boost priority for fundamental skills
        current_level = current_skills.get(skill, 0)
        if current_level < 30:
            base_priority *= 1.5

        # Boost priority for skills that others depend on
        dependency_boost = len(self._get_dependent_skills(skill)) * 0.1
        base_priority += dependency_boost

        return min(base_priority, 1.0)  # Cap at 1.0

    def _get_dependent_skills(self, skill: str) -> List[str]:
        """Get skills that depend on the given skill."""
        dependents = []
        for parent, children in self.skill_hierarchy.items():
            if skill in children:
                dependents.append(parent)
        return dependents

    def _estimate_gap_hours(self, total_gap_percentage: float) -> int:
        """
        Estimate hours needed to close skill gaps.

        Rough estimate: 10 hours per 10% proficiency increase for average skill.
        """
        return int(total_gap_percentage * 0.1)  # 10 hours per 10% gap

    def _generate_recommendations(self, top_gaps: List[Tuple[str, Dict]]) -> List[str]:
        """Generate learning recommendations based on top gaps."""
        recommendations = []

        for skill, gap_info in top_gaps:
            gap_size = gap_info['gap_size']
            current = gap_info['current']

            if current < 20:
                recommendations.append(f"Start with {skill} fundamentals - build strong base")
            elif current < 50:
                recommendations.append(f"Focus on intermediate {skill} concepts - bridge the {gap_size:.0f}% gap")
            else:
                recommendations.append(f"Advance {skill} to expert level - close remaining {gap_size:.0f}% gap")

        return recommendations

    def identify_learning_sequence(self, skill_gaps: Dict[str, Dict]) -> List[str]:
        """
        Identify optimal learning sequence based on skill dependencies.

        Args:
            skill_gaps: Dictionary of skill gaps from analyze_skill_gaps

        Returns:
            Ordered list of skills to learn
        """
        # Simple topological sort based on dependencies
        sequence = []
        remaining = list(skill_gaps.keys())

        while remaining:
            # Find skills with no unresolved dependencies
            available = []
            for skill in remaining:
                deps = self._get_dependencies(skill)
                if all(dep not in remaining for dep in deps):
                    available.append(skill)

            if not available:
                # Circular dependency or error - just pick the highest priority
                available = [max(remaining, key=lambda s: skill_gaps[s]['priority'])]

            # Pick the highest priority available skill
            next_skill = max(available, key=lambda s: skill_gaps[s]['priority'])
            sequence.append(next_skill)
            remaining.remove(next_skill)

        return sequence

    def _get_dependencies(self, skill: str) -> List[str]:
        """Get prerequisite skills for the given skill."""
        # This is a simplified version - in reality would need a more comprehensive dependency graph
        deps = []

        # Check if skill is a child in hierarchy
        for parent, children in self.skill_hierarchy.items():
            if skill in children:
                deps.append(parent)

        # Add domain-specific dependencies
        if skill == "Sim2Real Transfer":
            deps.extend(["Robotics", "Computer Vision"])
        elif skill == "Reinforcement Learning":
            deps.append("Control Systems")

        return deps

    def calculate_skill_progression(self, skill: str, current_level: float,
                                  hours_invested: int) -> Dict:
        """
        Calculate expected skill progression based on time invested.

        Args:
            skill: Skill name
            current_level: Current proficiency (0-100)
            hours_invested: Hours spent learning

        Returns:
            Progression estimate
        """
        # Simplified learning curve model
        # Assume logarithmic learning curve
        base_learning_rate = 0.1  # 10% improvement per 10 hours for beginners

        # Adjust for current level (harder to improve at higher levels)
        difficulty_multiplier = 1 + (current_level / 100)

        expected_improvement = (hours_invested / 10) * base_learning_rate / difficulty_multiplier
        expected_improvement = min(expected_improvement, 100 - current_level)

        new_level = current_level + expected_improvement

        return {
            "current_level": current_level,
            "hours_invested": hours_invested,
            "expected_new_level": round(new_level, 1),
            "improvement": round(expected_improvement, 1),
            "time_to_next_milestone": self._estimate_time_to_milestone(new_level)
        }

    def _estimate_time_to_milestone(self, current_level: float) -> int:
        """Estimate hours to next 25% milestone."""
        next_milestone = math.ceil(current_level / 25) * 25
        if next_milestone > 100:
            return 0

        gap = next_milestone - current_level
        # Estimate 20 hours per 10% improvement
        return int(gap * 2)