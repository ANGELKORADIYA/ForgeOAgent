import os
import json
import uuid
from datetime import datetime
import traceback
from typing import Dict, List, Any, Optional
from google import genai
import sys

from core.managers.pip_install_manager import PIPInstallManager
from core.managers.api_key_manager import GlobalAPIKeyManager
from core.managers.agent_manager import AgentManager
from core.class_analyzer import PyClassAnalyzer
from core.helpers import capture_print_output

from core.config_prompts import (
    DEFAULT_SYSTEM_INSTRUCTION,
    DEFAULT_OUTPUT_REQUIRED,
    DEFAULT_OUTPUT_PROPERTIES,
    DEFAULT_MODEL,
    DEFAULT_SAFETY_SETTINGS,
    MAIN_AGENT_SYSTEM_INSTRUCTION,
    MAIN_AGENT_OUTPUT_REQUIRED,
    MAIN_AGENT_OUTPUT_PROPERTIES,
    DEFAULT_SYSTEM_INSTRUCTION_SEARCH,)

from google.genai import types

from clients.gemini import GeminiLogger , GeminiContentManager , GeminiExecutor , GeminiInquirer

MCP_TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp", "tools"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
MAIN_AGENT_LOG_DIR = os.path.join(LOG_DIR, "executor")
AGENT_LOG_DIR = os.path.join(LOG_DIR, "inquirer")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MAIN_AGENT_LOG_DIR, exist_ok=True)
os.makedirs(AGENT_LOG_DIR, exist_ok=True)

class GeminiAPIClient(GeminiLogger,GeminiContentManager,GeminiExecutor,GeminiInquirer):
    def __init__(self, 
                 api_keys: Optional[List[str]] = None,
                 system_instruction: str = None,
                 output_required: List[str] = DEFAULT_OUTPUT_REQUIRED,
                 output_properties: Dict[str, types.Schema] = DEFAULT_OUTPUT_PROPERTIES,
                 model: str = DEFAULT_MODEL,
                 conversation_id: str = None,
                 safety_settings: List[types.SafetySetting] = DEFAULT_SAFETY_SETTINGS,
                 reference_json: Any = None,
                 new_content: bool = False):
        self.model = model
        self.output_required = output_required
        self.output_properties = output_properties
        self.safety_settings = safety_settings
        self.reference_json = reference_json
        self.new_content = new_content
        if api_keys is not None:
            GlobalAPIKeyManager.initialize(api_keys)
        
        if system_instruction:
            self.system_instruction = DEFAULT_SYSTEM_INSTRUCTION + "\n\n" + system_instruction
        else:
            self.system_instruction = None
        self.conversation_id = conversation_id
        # self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # self.conversation_id = conversation_id or f"agent_{self.timestamp}_{uuid.uuid4().hex[:8]}"
        # self.log_file = f"{LOG_DIR}/{self.conversation_id}.jsonl"
        # self._init_log_file()
        
            
        self._contents = []
        self.request_count = 0


    def _execute_generated_code(self, main_response: Dict[str, Any]) -> None:
            print("🚀 Starting Code Execution")
            print("=" * 50)
            
            try:
                python_code = main_response.get("python", "")
                if python_code.strip() == "":
                    return
                mcp_tools_classes = PyClassAnalyzer.get_all_classes(MCP_TOOLS_DIR)
                execution_globals = {
                    'GeminiAPIClient': GeminiAPIClient,
                    'types': types,
                    'genai': genai,
                    'json': json,
                    'os': os,
                    'datetime': datetime,
                    'PIPInstallManager': PIPInstallManager,
                    'traceback': traceback,  # Add traceback for error handling
                }
                execution_globals.update(mcp_tools_classes)
                execution_globals["execution_globals"] = execution_globals
                print("⚡ Executing generated Python code...")
                
                exec(python_code, execution_globals)
                print("-" * 30)
                # execution_print_sting = capture_print_output(lambda: exec(python_code, execution_globals))
                # print(execution_print_sting)
                # self._log_interaction("execution_print_sting :"+str(execution_print_sting),None,log_type="execution_print_string")

                print("-" * 30)
                print("✅ Code execution completed successfully!")
                
            except Exception as e:
                error_msg = f"❌ Execution failed: {str(e)}"
                print(error_msg)
                self._log_interaction("Error in Your Code :"+error_msg,None)
                print(f"📋 Traceback:\n{traceback.format_exc()}")


if __name__ == "__main__":
    print(GeminiAPIClient()._log_interaction)
    print(GeminiAPIClient()._get_last_conversation_id)
    print(GeminiAPIClient()._execute_generated_code)
    print(GeminiAPIClient().generate_content)
    print(GeminiAPIClient().search_content)