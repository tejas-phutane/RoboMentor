from typing import Dict, List, Optional
from .gpt_client import GPTClient


class QuizGenerator:
    """
    Generates quizzes using GPT-4o based on concepts, skills, or user notes.
    """

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client

    def generate_quiz(self, topic: str, difficulty: str = "intermediate",
                     num_questions: int = 5, context: Optional[Dict] = None) -> Dict:
        """
        Generate a quiz on a given topic.

        Args:
            topic: The topic to generate quiz for
            difficulty: Difficulty level (beginner, intermediate, advanced)
            num_questions: Number of questions to generate
            context: Optional context (user notes, skills, etc.)

        Returns:
            Quiz dictionary with questions and answers
        """
        prompt = self._build_quiz_prompt(topic, difficulty, num_questions, context)

        try:
            response = self.gpt_client.generate_text(prompt, max_tokens=2000, temperature=0.7)
            return self._parse_quiz_response(response)
        except Exception as e:
            return {"error": f"Failed to generate quiz: {str(e)}"}

    def generate_quiz_from_notes(self, notes: str, num_questions: int = 5) -> Dict:
        """
        Generate a quiz based on user's notes.

        Args:
            notes: User's notes content
            num_questions: Number of questions

        Returns:
            Quiz dictionary
        """
        prompt = f"""Based on the following notes, generate a {num_questions}-question quiz.
Focus on key concepts and important details from the notes.

Notes:
{notes}

Generate {num_questions} multiple-choice questions (4 options each) with correct answers.
Format as JSON with this structure:
{{
    "questions": [
        {{
            "question": "Question text",
            "options": ["A) Option1", "B) Option2", "C) Option3", "D) Option4"],
            "correct_answer": "A",
            "explanation": "Brief explanation"
        }}
    ]
}}"""

        try:
            response = self.gpt_client.generate_text(prompt, max_tokens=2000, temperature=0.7)
            return self._parse_quiz_response(response)
        except Exception as e:
            return {"error": f"Failed to generate quiz from notes: {str(e)}"}

    def _build_quiz_prompt(self, topic: str, difficulty: str, num_questions: int,
                          context: Optional[Dict] = None) -> str:
        """Build the quiz generation prompt."""
        prompt = f"""Generate a {difficulty} level quiz on the topic: {topic}

Create {num_questions} multiple-choice questions (4 options each) that test understanding of key concepts.

"""

        if context:
            if 'user_skills' in context:
                prompt += f"User's current skills: {', '.join(context['user_skills'])}\n"
            if 'learning_goals' in context:
                prompt += f"Learning goals: {', '.join(context['learning_goals'])}\n"

        prompt += """
Format the response as JSON with this exact structure:
{
    "title": "Quiz Title",
    "topic": "Topic Name",
    "difficulty": "difficulty_level",
    "questions": [
        {
            "question": "Question text here?",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correct_answer": "A",
            "explanation": "Why this is correct and brief explanation"
        }
    ]
}

Ensure questions are educational and progressively test deeper understanding."""

        return prompt

    def _parse_quiz_response(self, response: str) -> Dict:
        """Parse the AI response into structured quiz data."""
        try:
            # Try to extract JSON from the response
            import json
            # Look for JSON content in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback: return the raw response
                return {"raw_response": response}
        except json.JSONDecodeError:
            return {"raw_response": response, "parse_error": "Could not parse as JSON"}

    def evaluate_answer(self, question: Dict, user_answer: str) -> Dict:
        """
        Evaluate a user's answer to a quiz question.

        Args:
            question: Question dictionary
            user_answer: User's selected answer

        Returns:
            Evaluation result
        """
        correct = user_answer.upper() == question.get('correct_answer', '').upper()

        return {
            "correct": correct,
            "user_answer": user_answer,
            "correct_answer": question.get('correct_answer'),
            "explanation": question.get('explanation', 'No explanation provided')
        }