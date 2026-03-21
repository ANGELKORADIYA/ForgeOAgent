import os
import sys
from typing import List
from dotenv import load_dotenv
load_dotenv()

from forgeoagent.clients.gemini_engine import GeminiAPIClient
from forgeoagent.core.managers.security_manager import SecurityManager


# only import prompts to activate and have _system_instruction
from forgeoagent.controller.executor_controller import save_last_executor , print_available_executors , create_master_executor
from forgeoagent.controller.inquirer_controller import print_available_inquirers , auto_import_inquirers , inquirer_using_selected_system_instructions


# Usage - just call this once
auto_import_inquirers()

def main():
    # Initialize security system
    security = SecurityManager()
    security.start_monitoring()
    api_keys = []
    gemini_keys = os.getenv("GEMINI_API_KEYS")
    if gemini_keys:
        api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]

    args = sys.argv[1:]
    shell_enabled = "--main" in args
    
    # Handle system instruction arguments
    user_sys_instruction = None
    if "-si" in args or "--system-instruction" in args:
        si_index = args.index("-si") if "-si" in args else args.index("--system-instruction")
        if si_index + 1 < len(args):
            user_sys_instruction = args[si_index + 1]
    elif "-sif" in args or "--system-instruction-file" in args:
        sif_index = args.index("-sif") if "-sif" in args else args.index("--system-instruction-file")
        if sif_index + 1 < len(args):
            try:
                with open(args[sif_index + 1], 'r', encoding='utf-8') as f:
                    user_sys_instruction = f.read()
                print(f"📄 Loaded system instruction from: {args[sif_index + 1]}")
            except Exception as e:
                print(f"❌ Error reading system instruction file: {e}")
                sys.exit(1)
    
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
            si_index = args.index("-si") if "-si" in args else (args.index("--system-instruction") if "--system-instruction" in args else -1)
            sif_index = args.index("-sif") if "-sif" in args else (args.index("--system-instruction-file") if "--system-instruction-file" in args else -1)
            prompt_type = "None"
            if p_index != -1:
                prompt_type = args[p_index + 1]
            main_index = args.index("--main") if "--main" in args else -1
            # Collect indices to exclude
            exclude_indices = {p_index, p_index + 1 if p_index != -1 else p_index, main_index, n_index}
            if si_index != -1:
                exclude_indices.update({si_index, si_index + 1})
            if sif_index != -1:
                exclude_indices.update({sif_index, sif_index + 1})
            prompt_text = next(args[i] for i in range(len(args)) if i not in exclude_indices)
            create_master_executor(api_keys, prompt_text, shell_enabled=shell_enabled, selected_agent={"agent_name": prompt_type}, reference_agent_path=prompt_type, new_content=True if n_index != -1 else False, user_system_instruction=user_sys_instruction)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt> --main [-si <instruction> | -sif <file>]")
    elif "-p" in args:
        try:
            p_index = args.index("-p")
            n_index = args.index("--new") if "--new" in args else -1
            si_index = args.index("-si") if "-si" in args else (args.index("--system-instruction") if "--system-instruction" in args else -1)
            sif_index = args.index("-sif") if "-sif" in args else (args.index("--system-instruction-file") if "--system-instruction-file" in args else -1)
            prompt_type = args[p_index + 1]
            # Collect indices to exclude
            exclude_indices = {p_index, p_index + 1 if p_index != -1 else p_index, n_index}
            if si_index != -1:
                exclude_indices.update({si_index, si_index + 1})
            if sif_index != -1:
                exclude_indices.update({sif_index, sif_index + 1})
            prompt_text = next(args[i] for i in range(len(args)) if i not in exclude_indices)
            if n_index != -1:
                inquirer_using_selected_system_instructions(prompt_text, api_keys, prompt_type, new_content=True, user_system_instruction=user_sys_instruction)
            else:
                inquirer_using_selected_system_instructions(prompt_text, api_keys, prompt_type, new_content=False, user_system_instruction=user_sys_instruction)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt> [-si <instruction> | -sif <file>]")

    elif len(args) == 1:
        input_text = args[0]
        main_agent = GeminiAPIClient(api_keys=api_keys,new_content=True)
        response = main_agent.search_content(input_text)
        print(response)
    else:
        create_master_executor(api_keys, user_system_instruction=user_sys_instruction)
    security.stop_monitoring()


if __name__ == "__main__":
    main()