import os
from datetime import datetime
import traceback
from typing import Dict, List, Any, Optional

from core.managers.pip_install_manager import PIPInstallManager
from core.class_analyzer import PyClassAnalyzer

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

MCP_TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "mcp", "tools"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
MAIN_AGENT_LOG_DIR = os.path.join(LOG_DIR, "main_agent")
AGENT_LOG_DIR = os.path.join(LOG_DIR, "agent")
# os.makedirs(LOG_DIR, exist_ok=True)
# os.makedirs(MAIN_AGENT_LOG_DIR, exist_ok=True)
# os.makedirs(AGENT_LOG_DIR, exist_ok=True)


from clients.gemini_engine import GeminiAPIClient
from core.managers.agent_manager import AgentManager

def print_available_agents():
    """Print all saved agents from AgentManager."""
    agent_manager = AgentManager()
    agents = agent_manager.list_agents()  # Assumes this returns a list of agent dicts
    if not agents:
        print("No agents found.")
        return
    for idx, agent in enumerate(agents):
        print(f"{agent.get('agent_name', 'Unnamed')}")
    print("None")


def save_last_agent(agent_name: str = None):
    try:
        conversation_id = GeminiAPIClient._get_last_conversation_id('main_agent')
        if not agent_name:
            agent_name = conversation_id
    except:
        agent_name = conversation_id
    AgentManager().save_agent(
                    agent_name=agent_name,
                    conversation_id=conversation_id
                )


def create_master_agent(api_keys: List[str], user_request: str = None, reference_agent_path: str = None, selected_agent: Dict = None , shell_enabled:bool = False,new_content:bool = False) -> Dict[str, Any]:
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

        GEMINI_CLASS_ANALYZER =PyClassAnalyzer.analyze_dir(f"{os.path.join(os.path.dirname(__file__))}/../clients"'')
        MCP_CLASS_ANALYZER=PyClassAnalyzer.analyze_dir(MCP_TOOLS_DIR)

        main_agent_system_intruction = MAIN_AGENT_SYSTEM_INSTRUCTION % {"GEMINI_CLASS_ANALYZER": GEMINI_CLASS_ANALYZER,"MCP_CLASS_ANALYZER": MCP_CLASS_ANALYZER}

        main_agent = GeminiAPIClient(
            api_keys=api_keys,
            system_instruction=main_agent_system_intruction,
            output_required=MAIN_AGENT_OUTPUT_REQUIRED,
            output_properties=MAIN_AGENT_OUTPUT_PROPERTIES,
            conversation_id=conversation_id,
            reference_json=reference_agent_path or './merge_current_dir_agent',
            new_content=new_content
        )
        
        main_agent_response = main_agent.generate_content(user_request)
        
        # Check if imports are needed and install them
        imports = main_agent_response.get("imports", [])
        if imports:
            print(f"\n🔍 Detected required packages: {imports}")
            pip_result = PIPInstallManager(imports)
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