import os
import json
from typing import Dict, List, Any, Optional
from google import genai

from forgeoagent.core.managers.api_key_manager import GlobalAPIKeyManager

from forgeoagent.config import (
    DEFAULT_SYSTEM_INSTRUCTION,
)

from google.genai import types
from google.api_core.exceptions import Unauthenticated, ResourceExhausted, GoogleAPICallError

class GeminiExecutor:
    def generate_content(self, prompt: str, max_retries: int = 3, previous_conversation_log: bool = True,system_instruction:str = None) -> Dict[str, Any]:
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
            contents.extend(self._get_previous_conversation_contents('executor'))
        
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
                raise e
        
        raise Exception(f"Failed after {max_retries} retries")
    