from .gemini.gemini_logger import GeminiLogger
from .gemini.gemini_executor import GeminiExecutor
from .gemini.gemini_inquirer import GeminiInquirer 
from .gemini_engine import GeminiAPIClient


print(GeminiExecutor().generate_content)
print(GeminiInquirer().search_content)
print(GeminiLogger()._init_log_file)
print(GeminiLogger()._log_interaction)
print(GeminiAPIClient()._execute_generated_code)



from .gemini.gemini_content_manager import GeminiContentManager
print(GeminiContentManager()._get_last_conversation_id("inquirer")) # naming if not agent name provided
print(GeminiContentManager()._get_referenced_agent_json_contents("/home/userpc/Desktop/29/ForgeOAgent/forgeoagent/logs/inquirer")) # loading prompt type or saved agents only executor uses
print(GeminiContentManager()._get_previous_conversation_contents("inquirer")) # loading last first previous conversations
