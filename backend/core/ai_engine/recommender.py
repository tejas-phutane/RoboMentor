from typing import Dict, List, Optional
from .gpt_client import GPTClient


class Recommender:
    """
    Generates learning recommendations using GPT-4o.
    """

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    def generate_recommendations(self, user_profile: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Generate personalized learning recommendations.

        Args:
            user_profile: User's skills, goals, and progress
            context: Additional context (current projects, available time, etc.)

        Returns:
            Recommendations dictionary
        """
        prompt = self._build_recommendation_prompt(user_profile, context)

        try:
            response = self.gpt_client.generate_text(prompt, max_tokens=1500, temperature=0.7)
            return self._parse_recommendations(response)
        except Exception as e:
            return {"error": f"Failed to generate recommendations: {str(e)}"}

    def recommend_next_topic(self, current_skills: Dict[str, float],
                           goals: List[str], available_hours: int = 10) -> Dict:
        """
        Recommend the next topic to learn based on current skills and goals.

        Args:
            current_skills: Dictionary of skill names to proficiency levels (0-100)
            goals: List of learning goals
            available_hours: Available learning hours

        Returns:
            Next topic recommendation
        """
        prompt = f"""Based on the user's current skills and goals, recommend the next best topic to learn.

Current Skills (proficiency 0-100%):
{chr(10).join([f"- {skill}: {level}%" for skill, level in current_skills.items()])}

Learning Goals:
{chr(10).join([f"- {goal}" for goal in goals])}

Available learning time: {available_hours} hours this week

Recommend 1 primary topic and 2-3 supporting topics. Include:
- Why this topic is important
- Estimated time to learn
- Prerequisites
- Expected outcomes
- Learning resources

Format as JSON:
{{
    "primary_topic": {{
        "name": "Topic name",
        "reason": "Why learn this now",
        "estimated_hours": 5,
        "prerequisites": ["Skill1", "Skill2"],
        "expected_outcomes": ["Outcome1", "Outcome2"],
        "resources": ["Resource1", "Resource2"]
    }},
    "supporting_topics": [
        {{
            "name": "Topic name",
            "reason": "Why this supports the primary topic"
        }}
    ]
}}"""

        try:
            response = self.gpt_client.generate_text(prompt, max_tokens=1000, temperature=0.6)
            return self._parse_recommendations(response)
        except Exception as e:
            return {"error": f"Failed to recommend next topic: {str(e)}"}

    def _build_recommendation_prompt(self, user_profile: Dict, context: Optional[Dict] = None) -> str:
        """Build the recommendation generation prompt."""
        prompt = """You are an AI learning advisor. Generate personalized learning recommendations based on the user's profile.

"""

        # Add user profile information
        if 'skills' in user_profile:
            prompt += f"User Skills: {user_profile['skills']}\n"
        if 'goals' in user_profile:
            prompt += f"Learning Goals: {user_profile['goals']}\n"
        if 'progress' in user_profile:
            prompt += f"Current Progress: {user_profile['progress']}\n"

        # Add context
        if context:
            if 'current_projects' in context:
                prompt += f"Current Projects: {context['current_projects']}\n"
            if 'available_time' in context:
                prompt += f"Available Time: {context['available_time']} hours/week\n"
            if 'preferred_learning_style' in context:
                prompt += f"Learning Style: {context['preferred_learning_style']}\n"

        prompt += """
Generate comprehensive learning recommendations including:
1. Priority skills to focus on
2. Specific topics to learn next
3. Recommended learning sequence
4. Time estimates
5. Resources and materials
6. Potential projects to apply learning

Format the response as JSON with this structure:
{
    "priority_skills": ["Skill1", "Skill2", "Skill3"],
    "next_topics": [
        {
            "topic": "Topic name",
            "reason": "Why learn this",
            "difficulty": "Beginner/Intermediate/Advanced",
            "estimated_hours": 10,
            "prerequisites": ["Skill1"],
            "resources": ["Book: Title", "Course: Name", "Tutorial: Link"]
        }
    ],
    "learning_sequence": ["Step 1", "Step 2", "Step 3"],
    "recommended_projects": ["Project1", "Project2"],
    "time_allocation": {
        "theory": "30%",
        "practice": "50%",
        "projects": "20%"
    }
}"""

        return prompt

    def _parse_recommendations(self, response: str) -> Dict:
        """Parse the AI response into structured recommendations."""
        try:
            import json
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {"raw_response": response}
        except json.JSONDecodeError:
            return {"raw_response": response, "parse_error": "Could not parse as JSON"}