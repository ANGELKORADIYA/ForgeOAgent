from google.genai import types
import os
import dotenv
dotenv.load_dotenv()


MCP_TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp", "tools"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
MAIN_AGENT_LOG_DIR = os.path.join(LOG_DIR, "executor")
AGENT_LOG_DIR = os.path.join(LOG_DIR, "inquirer")
MCP_TOOLS_LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "mcp_tools"))


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_SAFETY_SETTINGS = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_LOW_AND_ABOVE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_LOW_AND_ABOVE"),
]