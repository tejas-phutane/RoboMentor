from typing import Dict, List, Optional
from .gpt_client import GPTClient


class ChatHandler:
    """
    Handles chat interactions with the AI mentor.
    """

    def __init__(self, gpt_client: GPTClient):
        self.gpt_client = gpt_client
        self.conversation_history: List[Dict[str, str]] = []

    def send_message(self, user_message: str, context: Optional[Dict] = None) -> str:
        """
        Send a message to the AI mentor and get a response.

        Args:
            user_message: User's message
            context: Optional context information (skills, goals, etc.)

        Returns:
            AI response
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        # Prepare system message with context
        system_message = self._build_system_message(context)

        # Prepare messages for API
        messages = [system_message] + self.conversation_history[-10:]  # Keep last 10 messages

        try:
            response = self.gpt_client.chat_completion(messages, temperature=0.7)
            ai_response = response['choices'][0]['message']['content']

            # Add AI response to history
            self.conversation_history.append({"role": "assistant", "content": ai_response})

            return ai_response
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    def _build_system_message(self, context: Optional[Dict] = None) -> Dict[str, str]:
        """
        Build the system message with context information.

        Args:
            context: Context dictionary with user information

        Returns:
            System message dictionary
        """
        base_prompt = """You are RoboMentor, an intelligent AI learning assistant specialized in robotics engineering.
You help users learn and master robotics concepts through personalized guidance, quiz generation, and learning path recommendations.

Your capabilities:
- Answer questions about robotics, AI, computer vision, and related fields
- Generate personalized quizzes based on user knowledge and goals
- Recommend learning resources and paths
- Track learning progress and provide feedback
- Adapt to user's skill level and learning style

Be encouraging, technical, and focused on hands-on learning."""

        if context:
            context_str = "\n\nUser Context:\n"
            if 'skills' in context:
                context_str += f"Skills: {', '.join(context['skills'])}\n"
            if 'goals' in context:
                context_str += f"Goals: {', '.join(context['goals'])}\n"
            if 'current_project' in context:
                context_str += f"Current Project: {context['current_project']}\n"
            base_prompt += context_str

        return {"role": "system", "content": base_prompt}

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history.copy()