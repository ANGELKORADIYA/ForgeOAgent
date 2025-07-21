import os
import sys
from dotenv import load_dotenv
from typing import List
from clients.gemini_client import main, GeminiAPIClient
from core.agent_manager import AgentManager
from core.security_manager import SecurityManager

load_dotenv()

# only import prompts to activate and have _system_instruction
from core.prompts.enhance_prompt import ENHANCE_PROMPT_SYSTEM_INSTRUCTION , ENHANCE_PROMPT_USER_INSTRUCTION
from core.prompts.enhance_text import ENHANCE_TEXT_SYSTEM_INSTRUCTION
from core.prompts.generate_email import GENERATE_EMAIL_SYSTEM_INSTRUCTION
from core.prompts.refine_code import REFINE_CODE as REFINE_CODE_SYSTEM_INSTRUCTION 
from core.prompts.regex import REGEX_SYSTEM_INSTRUCTION 
from core.prompts.what_word import WHAT_WORD_SYSTEM_INSTRUCTION 


def run_prompt_improvement(input_text: str, api_keys: List[str], prompt_agent: str,new_content:bool=False):
    """Run Gemini API prompt improvement using the given system instruction."""
    main_agent = GeminiAPIClient(api_keys=api_keys,new_content=new_content)
    prompt_agent = prompt_agent.strip().upper()
    if not prompt_agent.endswith("_SYSTEM_INSTRUCTION"):
        prompt_agent += "_SYSTEM_INSTRUCTION"
    system_prompt = globals().get(prompt_agent)
    if not system_prompt:
        print(f"[ERROR] No system instruction found for: {prompt_agent}")
        return

    prompt_agent = prompt_agent.replace("_SYSTEM_INSTRUCTION", "")
    user_enhance = globals().get(f"{prompt_agent}_USER_INSTRUCTION", "```user_input")
    query = f"{user_enhance} {input_text}```"
    response = main_agent.call_api_search(query, system_instruction=system_prompt)
    print(response)


def print_available_system_instructions():
    """Print all available *_SYSTEM_INSTRUCTION variables from the current context."""
    for var_name in globals():
        if var_name.endswith("_SYSTEM_INSTRUCTION"):
            print(f"{var_name}")

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
        print_available_agents()
    elif "-l" in args and not shell_enabled:
        print_available_system_instructions()
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
            main(api_keys,prompt_text,shell_enabled=shell_enabled,selected_agent={"agent_name":prompt_type},reference_agent_path=prompt_text_path)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt> --main")
    elif "-p" in args:
        try:
            p_index = args.index("-p")
            n_index = args.index("--new") if "--new" in args else -1
            prompt_type = args[p_index + 1]
            prompt_text = next(args[i] for i in range(len(args)) if i not in {p_index, p_index + 1 if not p_index == -1 else p_index,n_index})
            if n_index != -1:
                run_prompt_improvement(prompt_text, api_keys, prompt_type,new_content=True)
            else:
                run_prompt_improvement(prompt_text, api_keys, prompt_type,new_content=False)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt>")

    elif len(args) == 1:
        input_text = args[0]
        main_agent = GeminiAPIClient(api_keys=api_keys,new_content=True)
        response = main_agent.call_api_search(input_text)
        print(response)
    else:
        main(api_keys)
    security.stop_monitoring()
