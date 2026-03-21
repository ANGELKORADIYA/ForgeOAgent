from dataclasses import dataclass, field
from typing import Any

@dataclass
class GenerateRequest:
    prompt: str
    system_instruction: str | None = None
    model: str | None = None
    tools: list[Any] | None = None
    response_schema: dict | None = None
    conversation_id: str | None = None

@dataclass
class GenerateResult:
    text: str | None
    json_data: dict | None
    raw: Any
    usage: dict | None
    conversation_id: str | None

@dataclass
class ChatRequest:
    messages: list[dict]
    system_instruction: str | None = None
    model: str | None = None
    tools: list[Any] | None = None
    response_schema: dict | None = None
    conversation_id: str | None = None

@dataclass
class ChatResult:
    message: dict | None
    json_data: dict | None
    raw: Any
    usage: dict | None
    conversation_id: str | None
