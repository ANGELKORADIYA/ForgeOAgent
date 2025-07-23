import os
import json
import uuid
from datetime import datetime
import traceback
from typing import Dict, List, Any, Optional
from google import genai
import sys

from core.pip_installer import pip_installer
from core.api_key_manager import GlobalAPIKeyManager
from core.agent_manager import AgentManager
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
from google.api_core.exceptions import Unauthenticated, ResourceExhausted, GoogleAPICallError

# Ensure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
MAIN_AGENT_LOG_DIR = os.path.join(LOG_DIR, "main_agent")
AGENT_LOG_DIR = os.path.join(LOG_DIR, "agent")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MAIN_AGENT_LOG_DIR, exist_ok=True)
os.makedirs(AGENT_LOG_DIR, exist_ok=True)

class GeminiAPIClient:
    """Simplified Gemini API client with better error handling."""
    
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
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.conversation_id = conversation_id or f"agent_{self.timestamp}_{uuid.uuid4().hex[:8]}"
            
        self._contents = []
        self.request_count = 0
        self.log_file = f"{LOG_DIR}/{self.conversation_id}.jsonl"


        self._init_log_file()

    @staticmethod
    def _get_last_conversation_id(type:str = "agent") -> Optional[str]:
        """Gets the most recent conversation ID from the 'logs' directory."""
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", "logs", type))
        if not os.path.isdir(logs_dir):
            return None
        
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.jsonl') and f.startswith(f'{type}_')]
        if not log_files:
            return None
        
        try:
            full_paths = [os.path.join(logs_dir, f) for f in log_files]
            latest_file = max(full_paths, key=os.path.getmtime)
            return os.path.basename(latest_file)[:-6]  # Remove .jsonl
        except (ValueError, FileNotFoundError):
            return None
    
    def _init_log_file(self):
        """Initialize the log file with metadata."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                metadata = {
                    "type": "metadata",
                    "conversation_id": self.conversation_id,
                    "start_time": datetime.now().isoformat(),
                    "model": self.model
                }
                f.write(json.dumps(metadata) + "\n")
    
    def _log_interaction(self, prompt: str, response_data: Any, success: bool = True, error: str = None):
        """Log API interactions."""
        log_entry = {
            "type": "interaction",
            "timestamp": datetime.now().isoformat(),
            "request_count": self.request_count,
            "success": success,
            "input": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        }
        
        if success and response_data:
            if isinstance(response_data, dict):
                log_entry["response"] = response_data
            elif hasattr(response_data, 'text'):
                try:
                    log_entry["response"] = json.loads(response_data.text)
                except json.JSONDecodeError:
                    log_entry["response"] = response_data.text
            else:
                log_entry["response"] = str(response_data)
        
        if error:
            log_entry["error"] = error
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def _get_referenced_agent_json_contents(self, reference_folder: str) -> list:
        """Read all JSONL files in the reference folder and return as Gemini contents."""
        import glob
        contents = []
        if reference_folder and os.path.isdir(reference_folder):
            for file in glob.glob(os.path.join(reference_folder, '*.jsonl')):
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line)
                            # Add as a system or user message (customize as needed)
                            if isinstance(data, dict) and data.get('type') == 'interaction':
                                text = data.get('input', None)
                                if text is not None:
                                    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
                                assistant_text = data.get('response', None)
                                if assistant_text is not None:
                                    if isinstance(assistant_text, dict):
                                        assistant_text = json.dumps(assistant_text, ensure_ascii=False)
                                    contents.append(types.Content(role="model", parts=[types.Part.from_text(text=str(assistant_text))]))
                        except Exception:
                            continue
        return contents

    def _get_previous_conversation_contents(self,type:str = "agent") -> list:
        """Read previous conversation from the current log file and return as Gemini contents."""
        contents = []
        last_id = self._get_last_conversation_id(type)
        self.conversation_id = last_id or self.conversation_id or f"agent_{self.timestamp}_{uuid.uuid4().hex[:8]}"
        self.log_file = f"{LOG_DIR}/{type}/{self.conversation_id}.jsonl"

        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        if data.get('type') == 'interaction' and 'input' in data:
                            text = data['input']
                            contents.append(types.Content(role="user", parts=[types.Part.from_text(text=text)]))
                            assistant_text = data.get('response', None)
                            if assistant_text:
                                if isinstance(assistant_text, dict):
                                    assistant_text = json.dumps(assistant_text, ensure_ascii=False)
                                contents.append(types.Content(role="model", parts=[types.Part.from_text(text=str(assistant_text))]))
                    except Exception:
                        continue
        return contents

    def call_api(self, prompt: str, max_retries: int = 3, previous_conversation_log: bool = True,system_instruction:str = None) -> Dict[str, Any]:
        """Make API call with error handling and retry logic."""
        
        if system_instruction is not None:
            system_instruction = system_instruction.strip()
        elif system_instruction is None and self.system_instruction is not None:
            system_instruction = DEFAULT_SYSTEM_INSTRUCTION + "\n\n" + self.system_instruction
        else:
            system_instruction = DEFAULT_SYSTEM_INSTRUCTION
        
        self.request_count += 1
        manager = GlobalAPIKeyManager()

        # Build request contents
        contents = []
        # 1. Add reference JSON contents if provided
        if self.reference_json:
            contents.extend(self._get_referenced_agent_json_contents(self.reference_json))
        # 2. Add previous conversation
        if previous_conversation_log and not self.new_content:
            contents.extend(self._get_previous_conversation_contents('main_agent'))
        
        # 3. Add current conversation prompts
        contents.extend(self._contents)
        
        # 4. Add current prompt
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ))
        
        self._contents.append(contents[-1])
        
        # Print contents in a nice way: model:text
        print("\nConversation contents so far:")
        for c in contents:
            if hasattr(c, "role") and hasattr(c, "parts"):
                text = ""
            if c.parts and hasattr(c.parts[0], "text"):
                text = c.parts[0].text
            print(f"{c.role}: {text}")
        print("-" * 40)
        
        for retry in range(max_retries):
            api_key = None
            try:
                api_key = manager.get_current_key()
                
                # Configure generation
                generate_config = types.GenerateContentConfig(
                    safety_settings=self.safety_settings,
                    response_mime_type="application/json",
                    response_schema=genai.types.Schema(
                        type=genai.types.Type.OBJECT,
                        required=self.output_required,
                        properties=self.output_properties
                    ),
                    system_instruction=[
                        types.Part.from_text(text=system_instruction)
                    ]
                )
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=generate_config
                )
                
                if response.candidates and response.candidates[0].content:
                    try:
                        response_json = json.loads(response.text)
                        self._log_interaction(prompt, response_json, success=True)
                        print(f"✅ Response received successfully! Request from #{self.conversation_id}")
                        print(f"   - Explanation: {response_json.get('explanation', '')}")
                        print(f"   - Task IDs: {response_json.get('ids', [])}")
                        print(f"   - response: {response_json.get('response', [])}")
                        print(f"   - Code Length: {len(response_json.get('python', ''))} characters")
                        self._contents.append(types.Content(
                            role="model",
                            parts=[types.Part.from_text(text=json.dumps(response_json, ensure_ascii=False))]
                        ))
                        return response_json
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"Invalid JSON response: {e}"
                        self._log_interaction(prompt, response.text, success=False, error=error_msg)
                        raise ValueError(f"{error_msg}. Raw response: {response.text}")
                else:
                    error_msg = f"Empty response. Feedback: {response.prompt_feedback}"
                    self._log_interaction(prompt, None, success=False, error=error_msg)
                    raise ValueError(error_msg)
            
            except (Unauthenticated, ResourceExhausted, GoogleAPICallError) as e:
                error_msg = f"{e.code.name}: {e.details}"
                manager.mark_key_failed(api_key, error_msg)
                
                if manager.get_detailed_status()['active_keys'] == 0:
                    self._log_interaction(prompt, None, success=False, error="All API keys exhausted")
                    raise Exception(f"All API keys exhausted. Last error: {error_msg}")
                
                print(f"🔄 Retrying with different API key (attempt {retry + 1}/{max_retries})")
                continue
            
            except Exception as e:
                error_msg = str(e)
                self._log_interaction(prompt, None, success=False, error=error_msg)
                
                if any(keyword in error_msg.lower() for keyword in ["quota", "limit", "invalid", "unauthorized"]):
                    manager.mark_key_failed(api_key, error_msg)
                    if retry < max_retries - 1:
                        continue
                
                raise e
        
        raise Exception(f"Failed after {max_retries} retries")
    
    def call_api_search(self, prompt: str, max_retries: int = 3,system_instruction:str = None) -> Dict[str, Any]:
        """Make API call with error handling and retry logic."""
        
        if system_instruction is not None:
            system_instruction = system_instruction.strip()
        elif system_instruction is None and self.system_instruction is not None:
            system_instruction = DEFAULT_SYSTEM_INSTRUCTION_SEARCH + "\n\n" + self.system_instruction # Not Needed
        else:
            system_instruction = DEFAULT_SYSTEM_INSTRUCTION_SEARCH

        self.request_count += 1
        manager = GlobalAPIKeyManager()

        contents = []
        if not self.new_content:
            contents.extend(self._get_previous_conversation_contents('agent'))
            
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ))
        
        for retry in range(max_retries):
            api_key = None
            try:
                api_key = manager.get_current_key()
                # tools = [types.Tool(url_context=types.UrlContext())]
                # Configure generation
                generate_config = types.GenerateContentConfig(
                    system_instruction=[
                        types.Part.from_text(text=system_instruction)
                    ],
                    thinking_config = types.ThinkingConfig(thinking_budget=-1,),
                    # tools=tools,
                    response_mime_type="text/plain"
                )
                
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=generate_config
                )
                if response.candidates and response.candidates[0].content:
                    try:
                        self._log_interaction(prompt, response.text, success=True)
                        return response.text
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"Invalid JSON response: {e}"
                        self._log_interaction(prompt, response.text, success=False, error=error_msg)
                        raise ValueError(f"{error_msg}. Raw response: {response.text}")
                else:
                    error_msg = f"Empty response. Feedback: {response.prompt_feedback}"
                    self._log_interaction(prompt, None, success=False, error=error_msg)
                    raise ValueError(error_msg)
            
            except (Unauthenticated, ResourceExhausted, GoogleAPICallError) as e:
                error_msg = f"{e.code.name}: {e.details}"
                manager.mark_key_failed(api_key, error_msg)
                
                if manager.get_detailed_status()['active_keys'] == 0:
                    self._log_interaction(prompt, None, success=False, error="All API keys exhausted")
                    raise Exception(f"All API keys exhausted. Last error: {error_msg}")                
                continue
            
            except Exception as e:
                error_msg = str(e)
                self._log_interaction(prompt, None, success=False, error=error_msg)
                
                if any(keyword in error_msg.lower() for keyword in ["quota", "limit", "invalid", "unauthorized"]):
                    manager.mark_key_failed(api_key, error_msg)
                    if retry < max_retries - 1:
                        continue
                
                raise e
        
        raise Exception(f"Failed after {max_retries} retries")
    
    def _execute_generated_code(self, main_response: Dict[str, Any]) -> None:
        print("🚀 Starting Code Execution")
        print("=" * 50)
        
        try:
            python_code = main_response.get("python", "")
            if python_code.strip() == "":
                return
                    
            execution_globals = {
                'GeminiAPIClient': GeminiAPIClient,
                'types': types,
                'genai': genai,
                'json': json,
                'os': os,
                'datetime': datetime,
                'pip_installer': pip_installer,
            }
            execution_globals["execution_globals"] = execution_globals
            print("⚡ Executing generated Python code...")
            print("-" * 30)
            
            exec(python_code, execution_globals)
            
            print("-" * 30)
            print("✅ Code execution completed successfully!")
            
        except Exception as e:
            error_msg = f"❌ Execution failed: {str(e)}"
            print(error_msg)
            print(f"📋 Traceback:\n{traceback.format_exc()}")



def main(api_keys: List[str], user_request: str = None, reference_agent_path: str = None, selected_agent: Dict = None , shell_enabled:bool = False,new_content:bool = False) -> Dict[str, Any]:
    """Create the main agent responsible for generating Python code with interactive agent selection."""
    print("🚀 AI Agent System")
    print("=" * 60)
    
    # If no user_request provided, handle interactive selection
    if user_request is None and not shell_enabled and not selected_agent and not reference_agent_path:
        # Select agent or create new
        selected_agent, reference_agent_path = AgentManager().select_agent_or_create_new()
        
        # Get user request
        user_request = input("\n💬 Enter your request: ").strip()
        if not user_request:
            print("❌ No request provided. Exiting...")
            return {"status": "error", "error": "No request provided"}
    
        print("🎯 Main Agent System Starting")
        print("=" * 60)
        print(f"📥 User Request: {user_request}")
        if reference_agent_path:
            print(f"🔗 Using reference agent: {selected_agent['agent_name'] if selected_agent else 'Unknown'}")
        print("=" * 60)
    print("🧠 Creating Main Agent...")
    
    try:
        # Create conversation ID based on whether using existing agent or new
        if selected_agent:
            conversation_id = f"main_agent_from_{selected_agent['agent_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        else:
            conversation_id = f"main_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        main_agent = GeminiAPIClient(
            api_keys=api_keys,
            system_instruction=MAIN_AGENT_SYSTEM_INSTRUCTION,
            output_required=MAIN_AGENT_OUTPUT_REQUIRED,
            output_properties=MAIN_AGENT_OUTPUT_PROPERTIES,
            conversation_id=conversation_id,
            reference_json=reference_agent_path or './merge_current_dir_agent',
            new_content=new_content
        )
        
        main_agent_response = main_agent.call_api(user_request)
        
        # Check if imports are needed and install them
        imports = main_agent_response.get("imports", [])
        if imports:
            print(f"\n🔍 Detected required packages: {imports}")
            pip_result = pip_installer(imports)
            print(f"📦 Package installation result: {pip_result['status']}")
            
            if pip_result['status'] == 'partial_success' or pip_result['failed']:
                print("⚠️  Some packages failed to install. Proceeding with execution...")
        
        execution_result = main_agent._execute_generated_code(main_agent_response)
        print(f"✅ Task completed successfully!", execution_result)
        
        result = {
            "status": "success",
            "response": main_agent_response,
            "conversation_id": main_agent.conversation_id,
            "task_ids": main_agent_response.get("ids", [])
        }
        
        # Ask to save agent if successful
        if not shell_enabled:
            save_choice = input("\n💾 Save this agent for future use? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                agent_name = input("Enter agent name: ").strip()
                if agent_name:
                    agent_manager = AgentManager()
                    agent_manager.save_agent(
                        agent_name=agent_name,
                        conversation_id=result["conversation_id"],
                        task_ids=result["task_ids"]
                    )
                else:
                    print("❌ No agent name provided. Agent not saved.")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"❌ System Error: {error_result}")
        print(f"❌ Task failed!")
        return error_result

# Example of use
# def main_prompt_improver(input_text:str,api_keys:List[str]):
#     main_agent = GeminiAPIClient(
#             api_keys=api_keys,
#         )
#     main_agent_response = main_agent.call_api_search("improve this prompt :```text "+input_text+"```",system_instruction=PROMPT_IMPROVER_SYSTEM_INSTRUCTION)
#     print(main_agent_response)
#     # main_agent_first_response = next(iter(main_agent_response))
    