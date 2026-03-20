from .base import BaseAgent

class EEATAgent(BaseAgent):
    def analyze_page(self, content):
        prompt = self._load_prompt("eeat_analysis.md", content=content[:4000])
        if not prompt:
            return None
        return self.call_llm(prompt)
