from github import Github
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import os

logger = logging.getLogger(__name__)


class GitHubTrendsIntegration:
    """Fetches robotics development trends from GitHub."""

    ROBOTICS_KEYWORDS = [
        'robotics', 'robot', 'ros', 'gazebo', 'moveit', 'panda', 'ur5', 'abb',
        'kuka', 'franka', 'dobot', 'universal-robots', 'reinforcement-learning',
        'computer-vision', 'opencv', 'pytorch', 'tensorflow', 'slam', 'navigation',
        'path-planning', 'motion-planning', 'control-systems', 'pid', 'lqr',
        'mpc', 'sim2real', 'domain-randomization', 'object-detection', 'yolo',
        'ssd', 'faster-rcnn', 'pointnet', 'voxelnet', 'lidar', 'radar', 'imu'
    ]

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token (optional, increases rate limits)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.client = Github(self.token) if self.token else Github()

    def get_trending_repos(self, days_back: int = 30, max_results: int = 50) -> List[Dict]:
        """
        Fetch trending robotics repositories from GitHub.

        Args:
            days_back: Number of days to look back for activity
            max_results: Maximum number of repositories to return

        Returns:
            List of repository dictionaries with metadata
        """
        try:
            repos = []
            query_parts = []

            # Build query with robotics keywords
            for keyword in self.ROBOTICS_KEYWORDS[:5]:  # Limit to avoid too broad query
                query_parts.append(f'{keyword} in:name,description,topics')

            query = ' OR '.join(query_parts)
            query += f' created:>{(datetime.now() - timedelta(days=days_back)).date()}'

            # Search repositories
            results = self.client.search_repositories(
                query=query,
                sort='stars',
                order='desc'
            )

            for repo in results[:max_results]:
                repos.append({
                    'name': repo.name,
                    'full_name': repo.full_name,
                    'description': repo.description or '',
                    'url': repo.html_url,
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'language': repo.language,
                    'topics': repo.get_topics(),
                    'created_at': repo.created_at.isoformat() if repo.created_at else None,
                    'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
                    'owner': repo.owner.login,
                    'size': repo.size
                })

            logger.info(f"Fetched {len(repos)} trending repos from GitHub")
            return repos

        except Exception as e:
            logger.error(f"Error fetching GitHub repos: {e}")
            return []

    def get_recent_activity(self, repos: List[Dict], days_back: int = 7) -> Dict[str, List[Dict]]:
        """
        Get recent activity (commits, issues, PRs) for repositories.

        Args:
            repos: List of repository dictionaries
            days_back: Days to look back for activity

        Returns:
            Dictionary mapping repo names to activity lists
        """
        activity = {}
        since_date = datetime.now() - timedelta(days=days_back)

        for repo_data in repos[:10]:  # Limit to top 10 repos
            try:
                repo = self.client.get_repo(repo_data['full_name'])
                repo_activity = []

                # Get recent commits
                commits = repo.get_commits(since=since_date)
                for commit in commits[:5]:  # Last 5 commits
                    repo_activity.append({
                        'type': 'commit',
                        'message': commit.commit.message[:100],
                        'author': commit.commit.author.name if commit.commit.author else 'Unknown',
                        'date': commit.commit.author.date.isoformat() if commit.commit.author else None,
                        'url': commit.html_url
                    })

                # Get recent issues/PRs
                issues = repo.get_issues(since=since_date, state='all')
                for issue in issues[:3]:  # Last 3 issues
                    repo_activity.append({
                        'type': 'issue' if not issue.pull_request else 'pull_request',
                        'title': issue.title,
                        'state': issue.state,
                        'created_at': issue.created_at.isoformat(),
                        'url': issue.html_url
                    })

                activity[repo_data['name']] = repo_activity

            except Exception as e:
                logger.warning(f"Error getting activity for {repo_data['full_name']}: {e}")
                continue

        return activity

    def get_trending_topics(self, repos: List[Dict]) -> Dict[str, int]:
        """
        Extract trending topics from repository names, descriptions, and topics.

        Args:
            repos: List of repository dictionaries

        Returns:
            Dictionary of topics and their frequency
        """
        from collections import Counter

        topic_counts = Counter()

        for repo in repos:
            # Count topics
            for topic in repo.get('topics', []):
                topic_counts[topic] += 1

            # Count keywords in name and description
            text = (repo['name'] + ' ' + repo['description']).lower()
            for keyword in self.ROBOTICS_KEYWORDS:
                if keyword.replace('-', ' ') in text or keyword in text:
                    topic_counts[keyword] += 1

        return dict(topic_counts.most_common(10))

    def get_skill_recommendations(self, repos: List[Dict]) -> List[str]:
        """
        Generate skill upgrade recommendations based on trending repositories.

        Args:
            repos: List of repository dictionaries

        Returns:
            List of recommended skills to focus on
        """
        trending_topics = self.get_trending_topics(repos)

        # Map topics to skills
        skill_mappings = {
            'reinforcement-learning': 'Reinforcement Learning',
            'computer-vision': 'Computer Vision',
            'robotics': 'Robotics',
            'ros': 'ROS (Robot Operating System)',
            'slam': 'SLAM',
            'navigation': 'Robot Navigation',
            'motion-planning': 'Motion Planning',
            'control-systems': 'Control Systems',
            'pytorch': 'PyTorch',
            'tensorflow': 'TensorFlow',
            'opencv': 'OpenCV'
        }

        recommendations = []
        for topic, count in trending_topics.items():
            if topic in skill_mappings and count > 1:  # Threshold for significance
                skill = skill_mappings[topic]
                recommendations.append(f"Explore {skill} - popular in {count} trending repos")

        return recommendations[:5]  # Top 5 recommendations