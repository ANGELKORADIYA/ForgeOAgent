import os
import sys
from dotenv import load_dotenv
from typing import List
from clients.gemini_client import main, GeminiAPIClient
load_dotenv()

# only import prompts to activate and have _system_instruction
from core.prompts.enhance_prompt import ENHANCE_PROMPT_SYSTEM_INSTRUCTION
from core.prompts.enhance_text import ENHANCE_TEXT_SYSTEM_INSTRUCTION
from core.prompts.generate_email import GENERATE_EMAIL_SYSTEM_INSTRUCTION
from core.prompts.refine_code import REFINE_CODE as REFINE_CODE_SYSTEM_INSTRUCTION 


def run_prompt_improvement(input_text: str, api_keys: List[str], prompt_agent: str):
    """Run Gemini API prompt improvement using the given system instruction."""
    main_agent = GeminiAPIClient(api_keys=api_keys)
    prompt_agent = prompt_agent.strip().upper()
    if not prompt_agent.endswith("_SYSTEM_INSTRUCTION"):
        prompt_agent += "_SYSTEM_INSTRUCTION"
    system_prompt = globals().get(prompt_agent)
    if not system_prompt:
        print(f"[ERROR] No system instruction found for: {prompt_agent}")
        return

    query = f"improve this prompt :```text {input_text}```"
    response = main_agent.call_api_search(query, system_instruction=system_prompt)
    print(response)


def print_available_system_instructions():
    """Print all available *_SYSTEM_INSTRUCTION variables from the current context."""
    for var_name in globals():
        if var_name.endswith("_SYSTEM_INSTRUCTION"):
            print(f"{var_name}")


if __name__ == "__main__":
    api_keys = []
    gemini_keys = os.getenv("GEMINI_API_KEYS")
    if gemini_keys:
        api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]

    args = sys.argv[1:]

    if "-l" in args:
        print_available_system_instructions()

    elif "-p" in args:
        try:
            p_index = args.index("-p")
            prompt_type = args[p_index + 1]
            prompt_text = args[p_index + 2]
            run_prompt_improvement(prompt_text, api_keys, prompt_type)
        except (IndexError, ValueError):
            print("[ERROR] Usage: -p <type> <prompt>")

    elif len(args) == 1:
        input_text = args[0]
        run_prompt_improvement(input_text, api_keys, "ENHANCE_PROMPT_SYSTEM_INSTRUCTION")

    else:
        main(api_keys)
