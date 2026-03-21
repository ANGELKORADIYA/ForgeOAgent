class ForgeOAgentError(Exception):
    """Base exception for all ForgeOAgent errors."""
    pass

class ProviderError(ForgeOAgentError):
    """Raised when an LLM provider encounters an error."""
    pass

class AgentCreationError(ForgeOAgentError):
    """Raised when an agent cannot be created."""
    pass

class CodeExecutionError(ForgeOAgentError):
    """Raised when generated code fails to execute safely."""
    pass
