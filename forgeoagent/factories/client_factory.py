from forgeoagent.providers.registry import get_provider_class
from forgeoagent.providers.base.interfaces import BaseLLMProvider
from forgeoagent.config.defaults import default_settings

class ClientFactory:
    """Factory to instantiate LLM Providers based on configuration."""
    @staticmethod
    def create_client(provider_name: str = None) -> BaseLLMProvider:
        name = provider_name or default_settings.active_provider
        provider_cls = get_provider_class(name)
        return provider_cls()
