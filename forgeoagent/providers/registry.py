from typing import Dict, Type
from forgeoagent.providers.base.interfaces import BaseLLMProvider

PROVIDER_REGISTRY: Dict[str, Type[BaseLLMProvider]] = {}

def register_provider(name: str, provider_cls: Type[BaseLLMProvider]):
    PROVIDER_REGISTRY[name] = provider_cls

def get_provider_class(name: str) -> Type[BaseLLMProvider]:
    if name not in PROVIDER_REGISTRY:
        raise ValueError(f"Provider '{name}' not found in registry.")
    return PROVIDER_REGISTRY[name]
