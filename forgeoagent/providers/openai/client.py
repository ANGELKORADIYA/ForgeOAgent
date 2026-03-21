from forgeoagent.providers.base.interfaces import BaseLLMProvider
from forgeoagent.providers.base.models import GenerateRequest, GenerateResult, ChatRequest, ChatResult

class OpenAIProvider(BaseLLMProvider):
    """Adapter for OpenAI API."""
    def generate(self, request: GenerateRequest) -> GenerateResult:
        pass
    def chat(self, request: ChatRequest) -> ChatResult:
        pass
    def supports_tools(self) -> bool:
        return True
    def supports_json_mode(self) -> bool:
        return True
