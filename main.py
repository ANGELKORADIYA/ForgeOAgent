import os
import sys
from dotenv import load_dotenv
from typing import List
from clients.gemini_engine import GeminiAPIClient
from core.managers.agent_manager import AgentManager
from core.managers.security_manager import SecurityManager

load_dotenv()

# only import prompts to activate and have _system_instruction
import os
from controller.executor_controller import save_last_executor , print_available_executors , create_master_executor
from controller.inquirer_controller import print_available_inquirers , auto_import_inquirers , inquirer_using_selected_system_instructions


# Usage - just call this once
auto_import_inquirers()

if __name__ == "__main__":
    # Initialize security system
    security = SecurityManager()
    security.start_monitoring()
    api_keys = []
    gemini_keys = os.getenv("GEMINI_API_KEYS")
    if gemini_keys:
        api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]

    args = sys.argv[1:]
    shell_enabled = "--main" in args
    
    if "-l" in args and shell_enabled:
        print_available_executors()
    elif "-l" in args and not shell_enabled:
        print_available_inquirers()
    elif "--save" in args:
        agent_name = next(args[i] for i in range(len(args)) if i not in {args.index("--save") if "--save" in args else -1})
        save_last_executor(agent_name)
    elif shell_enabled:
        try:
            p_index = args.index("-p") if "-p" in args else -1
            n_index = args.index("--new") if "--new" in args else -1
            prompt_type = "None"
            if p_index != -1:
                prompt_type = args[p_index + 1]
            main_index = args.index("--main") if "--main" in args else -1
            # prompt_text = [args[i] for i in range(len(args)) if i != p_index and i != p_index + 1 and i != main_index][0]
            prompt_text = next(args[i] for i in range(len(args)) if i not in {p_index, p_index + 1 if not p_index == -1 else p_index, main_index,n_index})
            prompt_text_path = AgentManager().get_agent_path(prompt_type) if prompt_type else None
            create_master_executor(api_keys,prompt_text,shell_enabled=shell_enabled,selected_agent={"agent_name":prompt_type},reference_agent_path=prompt_text_path,new_content=True if n_index != -1 else False)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt> --main")
    elif "-p" in args:
        try:
            p_index = args.index("-p")
            n_index = args.index("--new") if "--new" in args else -1
            prompt_type = args[p_index + 1]
            prompt_text = next(args[i] for i in range(len(args)) if i not in {p_index, p_index + 1 if not p_index == -1 else p_index,n_index})
            if n_index != -1:
                inquirer_using_selected_system_instructions(prompt_text, api_keys, prompt_type,new_content=True)
            else:
                inquirer_using_selected_system_instructions(prompt_text, api_keys, prompt_type,new_content=False)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt>")

    elif len(args) == 1:
        input_text = args[0]
        main_agent = GeminiAPIClient(api_keys=api_keys,new_content=True)
        response = main_agent.search_content(input_text)
        print(response)
    else:
        create_master_executor(api_keys)
    security.stop_monitoring()
