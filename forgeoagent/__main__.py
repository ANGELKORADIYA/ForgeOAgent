from .core.main import main
# main()

## testiong 

from forgeoagent.config import config
print(config.DEFAULT_MODEL)

from forgeoagent.providers.gemini import client as gemini_engine
from forgeoagent.providers.gemini.client import GeminiAPIClient
print(GeminiAPIClient())

from forgeoagent.providers.gemini import gemini_content_manager
print(gemini_content_manager.GeminiContentManager)

from forgeoagent.controller import executor_controller
print(executor_controller.create_master_executor)

from forgeoagent.core.managers import security_manager
print(security_manager.SecurityManager)

from forgeoagent.core import PyClassAnalyzer
print(PyClassAnalyzer().get_all_classes("/home/userpc/29/ForgeOAgent/forgeoagent"))

## mcp tools testing

from forgeoagent.tools.implementations import structure_manager
memory_manager = structure_manager.StructureManager()
memory_manager.add_folder_structure("/home/userpc/29/ForgeOAgent/forgeoagent")
