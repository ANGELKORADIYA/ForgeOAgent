import os
import importlib
from typing import List

from clients.gemini_engine import GeminiAPIClient

def print_available_system_instructions():
    """Print all available *_SYSTEM_INSTRUCTION variables from the current context."""
    for var_name in globals():
        if var_name.endswith("_SYSTEM_INSTRUCTION"):
            print(f"{var_name}")

def auto_import_system_prompts(package_path="mcp.system_prompts"):
    """Auto import all constants from system_prompts modules"""
    globals_dict = globals()
    
    # Get directory path relative to current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(current_dir,"..", package_path.replace('.', os.sep))
    
    # Import all .py files
    for filename in os.listdir(dir_path):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"{package_path}.{module_name}")
                # Add only uppercase constants ending with SYSTEM_
                for name in dir(module):
                    if name.isupper() and name.endswith('_SYSTEM_INSTRUCTION') and not name.startswith('_'):
                        globals_dict[name] = getattr(module, name)
            except Exception as e:
                # print(f"✗ Failed to import {module_name}: {e}")
                pass

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
    response = main_agent.search_content(query, system_instruction=system_prompt)
    print(response)