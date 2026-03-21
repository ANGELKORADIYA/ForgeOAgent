from typing import Protocol
from .models import GenerateRequest, GenerateResult, ChatRequest, ChatResult

class BaseLLMProvider(Protocol):
    def generate(self, request: GenerateRequest) -> GenerateResult:
        ...

    def chat(self, request: ChatRequest) -> ChatResult:
        ...

    def supports_tools(self) -> bool:
        ...

    def supports_json_mode(self) -> bool:
        ...
