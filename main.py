from clients.gemini_client import main,main_prompt_improver

import sys
from dotenv import load_dotenv
import os

load_dotenv()
if __name__ == "__main__":
    # Load API keys from environment variable, splitting by comma if multiple keys are provided
    api_keys = []
    gemini_keys = os.getenv("GEMINI_API_KEYS")
    if gemini_keys:
        api_keys = [key.strip() for key in gemini_keys.split(",") if key.strip()]
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        main_prompt_improver(input_text,api_keys)
    else:
        main(api_keys)