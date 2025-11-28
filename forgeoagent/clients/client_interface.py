"""
Client Interface Definitions

This module defines Protocol-based interfaces for AI client implementations.
Using Protocol classes enables better IDE support, type checking, and method
reference tracking across inheritance hierarchies.
"""

from typing import Protocol, Dict, List, Any, Optional
from google.genai import types


class ILogger(Protocol):
    """Interface for logging functionality."""
    
    conversation_id: Optional[str]
    log_file: Optional[str]
    model: str
    request_count: int
    
    def _init_log_file(self, type: str = "inquirer") -> None:
        """Initialize the log file with metadata.
        
        Args:
            type: Type of logger (e.g., "inquirer", "executor")
        """
        ...
    
    def _log_interaction(
        self, 
        prompt: str, 
        response_data: Any, 
        success: bool = True, 
        error: Optional[str] = None,
        type: str = "inquirer",
        log_type: str = "interaction"
    ) -> None:
        """Log API interactions.
        
        Args:
            prompt: The input prompt
            response_data: The response data from the API
            success: Whether the interaction was successful
            error: Error message if any
            type: Type of interaction
            log_type: Type of log entry
        """
        ...


class IContentManager(Protocol):
    """Interface for content management functionality."""
    
    conversation_id: Optional[str]
    log_file: Optional[str]
    
    def _get_last_conversation_id(self, type: str = "inquirer") -> Optional[str]:
        """Gets the most recent conversation ID from the logs directory.
        
        Args:
            type: Type of conversation (e.g., "inquirer", "executor")
            
        Returns:
            The last conversation ID or None if not found
        """
        ...
    
    def _get_referenced_agent_json_contents(self, reference_folder: str) -> List[types.Content]:
        """Read all JSONL files in the reference folder and return as Gemini contents.
        
        Args:
            reference_folder: Path to the folder containing reference JSONL files
            
        Returns:
            List of Content objects for the API
        """
        ...
    
    def _get_previous_conversation_contents(self, type: str = "inquirer") -> List[types.Content]:
        """Read previous conversation from the current log file and return as Gemini contents.
        
        Args:
            type: Type of conversation (e.g., "inquirer", "executor")
            
        Returns:
            List of Content objects representing the conversation history
        """
        ...


class IExecutor(Protocol):
    """Interface for content generation/execution functionality."""
    
    system_instruction: Optional[str]
    model: str
    output_required: List[str]
    output_properties: Dict[str, types.Schema]
    safety_settings: List[types.SafetySetting]
    request_count: int
    conversation_id: Optional[str]
    reference_json: Any
    new_content: bool
    _contents: List[types.Content]
    
    def generate_content(
        self, 
        prompt: str, 
        max_retries: int = 3, 
        previous_conversation_log: bool = True,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make API call with error handling and retry logic.
        
        Args:
            prompt: The prompt to generate content for
            max_retries: Maximum number of retry attempts
            previous_conversation_log: Whether to include previous conversation
            system_instruction: Optional system instruction override
            
        Returns:
            Dictionary containing the generated response
        """
        ...


class IInquirer(Protocol):
    """Interface for search/inquiry functionality."""
    
    system_instruction: Optional[str]
    model: str
    request_count: int
    new_content: bool
    
    def search_content(
        self, 
        prompt: str, 
        max_retries: int = 3,
        system_instruction: Optional[str] = None
    ) -> str:
        """Make API call for search with error handling and retry logic.
        
        Args:
            prompt: The search prompt
            max_retries: Maximum number of retry attempts
            system_instruction: Optional system instruction override
            
        Returns:
            The search response text
        """
        ...


class IClientBase(ILogger, IContentManager, IExecutor, IInquirer, Protocol):
    """
    Combined interface that all AI clients should implement.
    
    This interface combines all component interfaces to define the complete
    contract for an AI client. Implementing this interface ensures:
    - IDE autocomplete works for all methods
    - Type checkers can validate implementations
    - "Find All References" works correctly in VS Code
    - Clear documentation of expected functionality
    """
    
    def _execute_generated_code(self, main_response: Dict[str, Any]) -> None:
        """Execute generated Python code from the API response.
        
        Args:
            main_response: The response dictionary containing Python code
        """
        ...
