import os
import dotenv
dotenv.load_dotenv()

from .config import MCP_TOOLS_DIR , LOG_DIR , MAIN_AGENT_LOG_DIR , AGENT_LOG_DIR , MCP_TOOLS_LOG_DIR
if os.getenv('ENV_STATUS','production') == 'development':
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(MAIN_AGENT_LOG_DIR, exist_ok=True)
    os.makedirs(AGENT_LOG_DIR, exist_ok=True)
    os.makedirs(MCP_TOOLS_LOG_DIR, exist_ok=True)

from .config import DEFAULT_MODEL , DEFAULT_SAFETY_SETTINGS


from .main_executor_prompts import MAIN_AGENT_SYSTEM_INSTRUCTION , MAIN_AGENT_OUTPUT_REQUIRED , MAIN_AGENT_OUTPUT_PROPERTIES
from .default_executor_prompts import DEFAULT_SYSTEM_INSTRUCTION , DEFAULT_OUTPUT_REQUIRED , DEFAULT_OUTPUT_PROPERTIES
from .default_inquirer_prompts import DEFAULT_SYSTEM_INSTRUCTION_SEARCH
