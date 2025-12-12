import arxiv
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ArXivTrendsIntegration:
    """Fetches robotics research trends from arXiv."""

    ROBOTICS_CATEGORIES = [
        'cs.RO',  # Robotics
        'cs.CV',  # Computer Vision
        'cs.AI',  # Artificial Intelligence
        'cs.LG',  # Machine Learning
        'cs.SY',  # Systems and Control
    ]

    def __init__(self):
        self.client = arxiv.Client()

    def get_recent_papers(self, days_back: int = 30, max_results: int = 50) -> List[Dict]:
        """
        Fetch recent robotics papers from arXiv.

        Args:
            days_back: Number of days to look back
            max_results: Maximum number of papers to return

        Returns:
            List of paper dictionaries with metadata
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            # Build search query for robotics categories
            query = ' OR '.join([f'cat:{cat}' for cat in self.ROBOTICS_CATEGORIES])

            # Create search
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )

            papers = []
            for result in self.client.results(search):
                # Filter by date
                if result.published >= start_date:
                    papers.append({
                        'title': result.title,
                        'authors': [author.name for author in result.authors],
                        'abstract': result.summary,
                        'published': result.published.isoformat(),
                        'url': result.pdf_url,
                        'categories': result.categories,
                        'doi': result.doi,
                        'comment': result.comment,
                        'journal_ref': result.journal_ref
                    })

            logger.info(f"Fetched {len(papers)} papers from arXiv")
            return papers

        except Exception as e:
            logger.error(f"Error fetching arXiv papers: {e}")
            return []

    def get_trending_topics(self, papers: List[Dict]) -> Dict[str, int]:
        """
        Extract trending topics from paper titles and abstracts.

        Args:
            papers: List of paper dictionaries

        Returns:
            Dictionary of topics and their frequency
        """
        from collections import Counter
        import re

        # Keywords to look for
        robotics_keywords = [
            'reinforcement learning', 'computer vision', 'robotics', 'control systems',
            'motion planning', 'sim2real', 'domain randomization', 'object detection',
            'slam', 'path planning', 'manipulation', 'grasping', 'navigation',
            'autonomous', 'machine learning', 'deep learning', 'neural networks',
            'optimization', 'simulation', 'real-time', 'safety', 'human-robot interaction'
        ]

        topic_counts = Counter()

        for paper in papers:
            text = (paper['title'] + ' ' + paper['abstract']).lower()

            for keyword in robotics_keywords:
                if keyword in text:
                    topic_counts[keyword] += 1

        return dict(topic_counts.most_common(10))

    def get_skill_recommendations(self, papers: List[Dict]) -> List[str]:
        """
        Generate skill upgrade recommendations based on trending papers.

        Args:
            papers: List of paper dictionaries

        Returns:
            List of recommended skills to focus on
        """
        trending_topics = self.get_trending_topics(papers)

        # Map topics to skills
        skill_mappings = {
            'reinforcement learning': 'Reinforcement Learning',
            'computer vision': 'Computer Vision',
            'robotics': 'Robotics',
            'control systems': 'Control Systems',
            'motion planning': 'Motion Planning',
            'sim2real': 'Sim2Real Transfer',
            'object detection': 'Object Detection',
            'slam': 'SLAM',
            'path planning': 'Path Planning',
            'manipulation': 'Robotic Manipulation',
            'machine learning': 'Machine Learning',
            'deep learning': 'Deep Learning'
        }

        recommendations = []
        for topic, count in trending_topics.items():
            if topic in skill_mappings and count > 2:  # Threshold for significance
                skill = skill_mappings[topic]
                recommendations.append(f"Focus on {skill} - trending in {count} recent papers")

        return recommendations[:5]  # Top 5 recommendations