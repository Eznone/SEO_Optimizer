import httpx
import logging
import os
import json
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)

class BaseAgent:
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, user=None):
        self.user = user
        self.api_key = self._get_api_key()
        self.prompts_dir = Path(__file__).resolve().parent / "prompts"

    def _get_api_key(self):
        """Fetches the Groq API key from user profile or env."""
        if self.user and hasattr(self.user, 'profile'):
            if self.user.profile.groq_api_key:
                return self.user.profile.groq_api_key
        return os.getenv("GROQ_API_KEY")

    def _load_prompt(self, filename, **kwargs):
        """Loads a prompt from a file and injects variables."""
        file_path = self.prompts_dir / filename
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                template = f.read()
            return template.format(**kwargs)
        except Exception as e:
            logger.error(f"Error loading prompt {filename}: {e}")
            return None

    def call_llm(self, prompt, model=None, response_format={"type": "json_object"}):
        """Executes a call to the Groq API."""
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set, cannot call LLM.")
            return None

        try:
            with httpx.Client() as client:
                response = client.post(
                    self.GROQ_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model or self.DEFAULT_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": response_format
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data['choices'][0]['message']['content']
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return content
                else:
                    logger.error(f"Groq API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None
