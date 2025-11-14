import os
import json
from typing import Dict, List, Any, Optional
from google import genai

from forgeoagent.core.managers.api_key_manager import GlobalAPIKeyManager

from forgeoagent.config import (
    DEFAULT_SYSTEM_INSTRUCTION_SEARCH,
)

from google.genai import types
from google.api_core.exceptions import Unauthenticated, ResourceExhausted, GoogleAPICallError


class GeminiInquirer:
    def search_content(self, prompt: str, max_retries: int = 3,system_instruction:str = None) -> Dict[str, Any]:
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
            contents.extend(self._get_previous_conversation_contents("inquirer"))
            
        contents.append(types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        ))
        
        for retry in range(max_retries):
            api_key = None
            try:
                api_key = manager.get_current_key()
                tools = [
                    types.Tool(googleSearch=types.GoogleSearch()),
                    # types.Tool(url_context=types.UrlContext()),
                    ]
                # Configure generation
                generate_config = types.GenerateContentConfig(
                    thinking_config = types.ThinkingConfig(thinking_budget=-1,),
                    response_mime_type="text/plain",
                    tools=tools,
                    system_instruction=[
                        types.Part.from_text(text=system_instruction)
                    ],
                    
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
                
                print(f"🔄 Retrying with different API key (attempt {retry + 1}/{max_retries})")
                continue
            
            except Exception as e:
                error_msg = str(e)
                self._log_interaction(prompt, None, success=False, error=error_msg)
                
                raise e
        
        raise Exception(f"Failed after {max_retries} retries")
    