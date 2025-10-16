import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from google.genai import types

LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))

class GeminiContents:
    @staticmethod
    def _get_last_conversation_id(type:str = "agent") -> Optional[str]:
        """Gets the most recent conversation ID from the 'logs' directory."""
        logs_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","..", "logs", type))
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
        self.conversation_id = last_id or self.conversation_id or f"{type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}"
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
