from forgeoagent.providers.base.interfaces import BaseLLMProvider

class AIService:
    """Service to interact with the LLM providers."""
    def __init__(self, provider: BaseLLMProvider):
        self.provider = provider

    def execute_prompt(self, prompt: str):
        pass
