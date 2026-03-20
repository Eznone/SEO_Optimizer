from .base import BaseAgent
import json

class TechnicalAgent(BaseAgent):
    def check_toxic_links(self, links_list):
        """Analyzes a list of URLs for potential toxicity."""
        prompt = self._load_prompt("toxic_links_analysis.md", links=json.dumps(links_list))
        if not prompt:
            return None
        return self.call_llm(prompt)
