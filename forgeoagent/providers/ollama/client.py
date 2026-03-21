from forgeoagent.providers.base.interfaces import BaseLLMProvider
from forgeoagent.providers.base.models import GenerateRequest, GenerateResult, ChatRequest, ChatResult

class OllamaProvider(BaseLLMProvider):
    """Adapter for local Ollama models."""
    def generate(self, request: GenerateRequest) -> GenerateResult:
        pass
    def chat(self, request: ChatRequest) -> ChatResult:
        pass
    def supports_tools(self) -> bool:
        return False
    def supports_json_mode(self) -> bool:
        return True
