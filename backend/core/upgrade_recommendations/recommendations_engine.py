from typing import Dict, List, Optional, Any
from ..learning_tracker.skill_analyzer import SkillAnalyzer
from ...integrations.trend_integrations.arxiv_trends import ArXivTrendsIntegration
from ...integrations.trend_integrations.github_trends import GitHubTrendsIntegration
import logging

logger = logging.getLogger(__name__)


class UpgradeRecommendationsEngine:
    """
    Engine for analyzing skill gaps and generating upgrade recommendations
    based on current skills, target goals, and real-time robotics trends.
    """

    def __init__(self):
        self.skill_analyzer = SkillAnalyzer()
        self.arxiv_trends = ArXivTrendsIntegration()
        self.github_trends = GitHubTrendsIntegration()

    def generate_upgrade_recommendations(self,
                                       current_skills: Dict[str, float],
                                       target_skills: Dict[str, float],
                                       days_back: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive upgrade recommendations.

        Args:
            current_skills: Current proficiency levels (0-100)
            target_skills: Target proficiency levels (0-100)
            days_back: Days to look back for trends

        Returns:
            Dictionary containing recommendations, gaps, and trends
        """
        try:
            # Analyze skill gaps
            skill_gaps = self.skill_analyzer.analyze_skill_gaps(current_skills, target_skills)

            # Fetch current trends
            arxiv_papers = self.arxiv_trends.get_recent_papers(days_back=days_back, max_results=100)
            github_repos = self.github_trends.get_trending_repos(days_back=days_back, max_results=50)

            # Extract trending topics
            arxiv_topics = self.arxiv_trends.get_trending_topics(arxiv_papers)
            github_topics = self.github_trends.get_trending_topics(github_repos)

            # Generate trend-based skill recommendations
            trend_recommendations = self._combine_trend_recommendations(arxiv_topics, github_topics)

            # Generate upgrade suggestions
            upgrade_suggestions = self._generate_upgrade_suggestions(
                skill_gaps, arxiv_topics, github_topics, arxiv_papers, github_repos
            )

            # Prioritize suggestions
            prioritized_suggestions = self._prioritize_suggestions(upgrade_suggestions, skill_gaps)

            return {
                "skill_gaps": skill_gaps,
                "trends": {
                    "arxiv_topics": arxiv_topics,
                    "github_topics": github_topics,
                    "arxiv_papers_count": len(arxiv_papers),
                    "github_repos_count": len(github_repos)
                },
                "upgrade_suggestions": prioritized_suggestions,
                "trend_recommendations": trend_recommendations,
                "learning_path": self._create_learning_path(prioritized_suggestions, skill_gaps)
            }

        except Exception as e:
            logger.error(f"Error generating upgrade recommendations: {e}")
            return {"error": str(e)}

    def _combine_trend_recommendations(self, arxiv_topics: Dict[str, int],
                                     github_topics: Dict[str, int]) -> List[str]:
        """Combine and deduplicate trend-based skill recommendations."""
        arxiv_recs = self.arxiv_trends.get_skill_recommendations([])
        github_recs = self.github_trends.get_skill_recommendations([])

        # Create mapping of skills to sources
        skill_sources = {}

        for rec in arxiv_recs + github_recs:
            # Extract skill name from recommendation
            if 'Focus on' in rec:
                skill = rec.split(' - ')[0].replace('Focus on ', '')
            elif 'Explore' in rec:
                skill = rec.split(' - ')[0].replace('Explore ', '')
            else:
                continue

            if skill not in skill_sources:
                skill_sources[skill] = []
            source = 'arXiv' if rec in arxiv_recs else 'GitHub'
            skill_sources[skill].append(source)

        # Create combined recommendations
        combined = []
        for skill, sources in skill_sources.items():
            sources_str = ', '.join(set(sources))
            combined.append(f"Upgrade {skill} - trending on {sources_str}")

        return combined[:5]

    def _generate_upgrade_suggestions(self, skill_gaps: Dict,
                                    arxiv_topics: Dict[str, int],
                                    github_topics: Dict[str, int],
                                    arxiv_papers: List[Dict],
                                    github_repos: List[Dict]) -> List[Dict]:
        """Generate specific upgrade suggestions combining gaps and trends."""
        suggestions = []

        # Map trending topics to skills
        topic_to_skill = {
            'reinforcement learning': 'Reinforcement Learning',
            'computer vision': 'Computer Vision',
            'robotics': 'Robotics',
            'control systems': 'Control Systems',
            'motion planning': 'Motion Planning',
            'sim2real': 'Sim2Real Transfer',
            'object detection': 'Object Detection',
            'slam': 'SLAM',
            'path planning': 'Path Planning',
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning',
            'ros': 'ROS',
            'pytorch': 'PyTorch',
            'tensorflow': 'TensorFlow'
        }

        # For each skill gap, check if it's trending
        for skill_name, gap_info in skill_gaps.get('gaps', {}).items():
            gap_size = gap_info['gap_size']
            current_level = gap_info['current']

            # Check if skill is trending
            trending_score = 0
            trend_sources = []

            for topic, count in arxiv_topics.items():
                if topic in topic_to_skill and topic_to_skill[topic] == skill_name:
                    trending_score += count
                    trend_sources.append('arXiv')

            for topic, count in github_topics.items():
                if topic in topic_to_skill and topic_to_skill[topic] == skill_name:
                    trending_score += count
                    trend_sources.append('GitHub')

            # Generate suggestion
            suggestion = {
                "skill": skill_name,
                "current_level": current_level,
                "gap_size": gap_size,
                "trending_score": trending_score,
                "trend_sources": list(set(trend_sources)),
                "priority": self._calculate_upgrade_priority(gap_size, current_level, trending_score),
                "reason": self._generate_reason(skill_name, gap_size, trending_score, trend_sources),
                "resources": self._find_relevant_resources(skill_name, arxiv_papers, github_repos)
            }

            suggestions.append(suggestion)

        return suggestions

    def _calculate_upgrade_priority(self, gap_size: float, current_level: float,
                                  trending_score: int) -> float:
        """Calculate priority score for upgrade suggestion."""
        # Base priority from gap size
        priority = gap_size / 100

        # Boost for low current levels
        if current_level < 30:
            priority *= 1.5

        # Boost for trending topics
        if trending_score > 0:
            priority *= (1 + trending_score * 0.1)

        return min(priority, 1.0)

    def _generate_reason(self, skill: str, gap_size: float, trending_score: int,
                        trend_sources: List[str]) -> str:
        """Generate human-readable reason for the upgrade suggestion."""
        reasons = []

        if gap_size > 50:
            reasons.append(f"significant skill gap of {gap_size:.0f}%")
        elif gap_size > 20:
            reasons.append(f"moderate skill gap of {gap_size:.0f}%")

        if trending_score > 0:
            sources_str = ', '.join(trend_sources)
            reasons.append(f"currently trending on {sources_str}")

        if not reasons:
            reasons.append("fundamental robotics skill")

        return " and ".join(reasons)

    def _find_relevant_resources(self, skill: str, arxiv_papers: List[Dict],
                               github_repos: List[Dict]) -> Dict[str, List[str]]:
        """Find relevant papers and repos for a skill."""
        resources = {"papers": [], "repositories": []}

        # Find relevant papers
        skill_lower = skill.lower()
        for paper in arxiv_papers[:10]:  # Check top 10 papers
            text = (paper['title'] + ' ' + paper['abstract']).lower()
            if skill_lower in text or any(keyword in text for keyword in skill_lower.split()):
                resources["papers"].append({
                    "title": paper['title'],
                    "url": paper['url']
                })

        # Find relevant repos
        for repo in github_repos[:10]:  # Check top 10 repos
            text = (repo['name'] + ' ' + repo['description']).lower()
            topics = [t.lower() for t in repo.get('topics', [])]
            if (skill_lower in text or
                any(keyword in text for keyword in skill_lower.split()) or
                skill_lower.replace(' ', '-') in topics):
                resources["repositories"].append({
                    "name": repo['name'],
                    "url": repo['url'],
                    "stars": repo['stars']
                })

        return resources

    def _prioritize_suggestions(self, suggestions: List[Dict],
                              skill_gaps: Dict) -> List[Dict]:
        """Sort suggestions by priority."""
        return sorted(suggestions, key=lambda x: x['priority'], reverse=True)

    def _create_learning_path(self, suggestions: List[Dict], skill_gaps: Dict) -> List[Dict]:
        """Create a structured learning path from suggestions."""
        # Use skill analyzer to create sequence
        skill_levels = {s['skill']: s['current_level'] for s in suggestions}
        target_levels = {s['skill']: float(min(100, s['current_level'] + s['gap_size']))
                        for s in suggestions}

        sequence = self.skill_analyzer.identify_learning_sequence(
            self.skill_analyzer.analyze_skill_gaps(skill_levels, target_levels)['gaps']
        )

        learning_path = []
        for skill in sequence:
            suggestion = next((s for s in suggestions if s['skill'] == skill), None)
            if suggestion:
                learning_path.append({
                    "skill": skill,
                    "estimated_hours": int(suggestion['gap_size'] * 0.1),  # Rough estimate
                    "prerequisites": self.skill_analyzer._get_dependencies(skill),
                    "resources": suggestion['resources']
                })

        return learning_path