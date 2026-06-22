"""
Unit tests for AI Engine module components.
"""

import pytest
from unittest.mock import Mock, patch
from ...core.ai_engine.gpt_client import GPTClient
from ...core.ai_engine.chat_handler import ChatHandler
from ...core.ai_engine.quiz_generator import QuizGenerator
from ...core.ai_engine.recommender import Recommender


class TestGPTClient:
    """Test GPT client functionality."""

    def test_init_with_api_key(self, mock_openai_key):
        """Test GPT client initialization with API key."""
        client = GPTClient("test-key")
        assert client.api_key == "test-key"
        assert client.base_url == "https://openrouter.ai/api/v1"

    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises ValueError."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="OpenRouter API key is required"):
                GPTClient(api_key=None)

    @patch('requests.post')
    def test_chat_completion_success(self, mock_post, mock_openai_key):
        """Test successful chat completion."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_post.return_value = mock_response

        client = GPTClient()
        result = client.chat_completion([{"role": "user", "content": "Hello"}])

        assert result["choices"][0]["message"]["content"] == "Test response"
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_chat_completion_failure(self, mock_post, mock_openai_key):
        """Test chat completion with API failure."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        client = GPTClient()
        with pytest.raises(Exception, match="API request failed"):
            client.chat_completion([{"role": "user", "content": "Hello"}])

    def test_generate_text(self, mock_gpt_client):
        """Test text generation."""
        result = mock_gpt_client.generate_text("Prompt")
        assert result == "Mock generated text"
        mock_gpt_client.chat_completion.assert_called_once()


class TestChatHandler:
    """Test chat handler functionality."""

    def test_init(self, mock_gpt_client):
        """Test chat handler initialization."""
        handler = ChatHandler(mock_gpt_client)
        assert handler.gpt_client == mock_gpt_client
        assert handler.conversation_history == []

    def test_send_message(self, mock_gpt_client):
        """Test sending message and getting response."""
        mock_gpt_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "AI response"}}]
        }

        handler = ChatHandler(mock_gpt_client)
        response = handler.send_message("Hello")

        assert response == "AI response"
        assert len(handler.conversation_history) == 2
        assert handler.conversation_history[0]["role"] == "user"
        assert handler.conversation_history[1]["role"] == "assistant"

    def test_send_message_with_context(self, mock_gpt_client):
        """Test sending message with user context."""
        mock_gpt_client.chat_completion.return_value = {
            "choices": [{"message": {"content": "Contextual response"}}]
        }

        handler = ChatHandler(mock_gpt_client)
        context = {"skills": ["Python"], "goals": ["Learn ML"]}
        response = handler.send_message("Hello", context)

        assert response == "Contextual response"
        # Check that system message includes context
        call_args = mock_gpt_client.chat_completion.call_args[0][0]
        system_message = call_args[0]
        assert "Python" in system_message["content"]
        assert "Learn ML" in system_message["content"]

    def test_clear_history(self, mock_gpt_client):
        """Test clearing conversation history."""
        handler = ChatHandler(mock_gpt_client)
        handler.conversation_history = [{"role": "user", "content": "test"}]
        handler.clear_history()
        assert handler.conversation_history == []


class TestQuizGenerator:
    """Test quiz generator functionality."""

    def test_init(self, mock_gpt_client):
        """Test quiz generator initialization."""
        generator = QuizGenerator(mock_gpt_client)
        assert generator.gpt_client == mock_gpt_client

    def test_generate_quiz(self, mock_gpt_client):
        """Test quiz generation."""
        mock_gpt_client.generate_text.return_value = '{"title": "Test Quiz", "questions": []}'

        generator = QuizGenerator(mock_gpt_client)
        result = generator.generate_quiz("Python", "intermediate", 3)

        assert "title" in result
        assert "questions" in result
        mock_gpt_client.generate_text.assert_called_once()

    def test_generate_quiz_from_notes(self, mock_gpt_client):
        """Test quiz generation from notes."""
        mock_gpt_client.generate_text.return_value = '{"questions": []}'

        generator = QuizGenerator(mock_gpt_client)
        result = generator.generate_quiz_from_notes("Some notes", 2)

        assert "questions" in result
        mock_gpt_client.generate_text.assert_called_once()

    def test_evaluate_answer_correct(self):
        """Test correct answer evaluation."""
        generator = QuizGenerator(Mock())
        question = {
            "correct_answer": "A",
            "explanation": "Test explanation"
        }

        result = generator.evaluate_answer(question, "A")
        assert result["correct"] is True
        assert result["user_answer"] == "A"
        assert result["correct_answer"] == "A"

    def test_evaluate_answer_incorrect(self):
        """Test incorrect answer evaluation."""
        generator = QuizGenerator(Mock())
        question = {
            "correct_answer": "A",
            "explanation": "Test explanation"
        }

        result = generator.evaluate_answer(question, "B")
        assert result["correct"] is False
        assert result["user_answer"] == "B"
        assert result["correct_answer"] == "A"


class TestRecommender:
    """Test recommender functionality."""

    def test_init(self, mock_gpt_client):
        """Test recommender initialization."""
        recommender = Recommender(mock_gpt_client)
        assert recommender.gpt_client == mock_gpt_client

    def test_generate_recommendations(self, mock_gpt_client):
        """Test recommendation generation."""
        mock_gpt_client.generate_text.return_value = '{"priority_skills": ["Python"], "next_topics": []}'

        recommender = Recommender(mock_gpt_client)
        user_profile = {"skills": ["Python"], "goals": ["Learn ML"]}
        result = recommender.generate_recommendations(user_profile)

        assert "priority_skills" in result
        assert "next_topics" in result
        mock_gpt_client.generate_text.assert_called_once()

    def test_recommend_next_topic(self, mock_gpt_client):
        """Test next topic recommendation."""
        mock_gpt_client.generate_text.return_value = '{"primary_topic": {"name": "ML"}}'

        recommender = Recommender(mock_gpt_client)
        current_skills = {"Python": 80.0}
        goals = ["Learn ML"]
        result = recommender.recommend_next_topic(current_skills, goals)

        assert "primary_topic" in result
        mock_gpt_client.generate_text.assert_called_once()