import requests
import json
from typing import Dict, List, Optional
import os


class GPTClient:
    """
    Client for interacting with GPT-4o via OpenRouter API.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, messages: List[Dict[str, str]], model: str = "openai/gpt-4o", **kwargs) -> Dict:
        """
        Send a chat completion request to GPT-4o.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (default: openai/gpt-4o)
            **kwargs: Additional parameters for the API

        Returns:
            API response as dictionary
        """
        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")

        return response.json()

    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using GPT-4o.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(
            messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response['choices'][0]['message']['content']

    def get_embedding(self, text: str) -> List[float]:
        """
        Get embeddings for text (if supported by the model).

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        # Note: This is a placeholder. OpenRouter may not support embeddings directly.
        # You might need to use a different service or model for embeddings.
        raise NotImplementedError("Embeddings not implemented for OpenRouter API")