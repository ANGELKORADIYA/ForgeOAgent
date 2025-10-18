import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

MCP_TOOLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "mcp", "tools"))
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
MAIN_AGENT_LOG_DIR = os.path.join(LOG_DIR, "main_agent")
AGENT_LOG_DIR = os.path.join(LOG_DIR, "agent")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MAIN_AGENT_LOG_DIR, exist_ok=True)
os.makedirs(AGENT_LOG_DIR, exist_ok=True)

class GeminiLogHandler:
    def _init_log_file(self,type:str = "agent"):
        """Initialize the log file with metadata."""
        if not self.conversation_id:
            self.conversation_id = f"{type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}_{uuid.uuid4().hex[:8]}"
            
        if "main_agent" == type or "main_agent" in self.conversation_id:
            self.log_file = os.path.join(MAIN_AGENT_LOG_DIR, f"{self.conversation_id}.jsonl")
        else:
            self.log_file = os.path.join(AGENT_LOG_DIR, f"{self.conversation_id}.jsonl")
            
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                metadata = {
                    "type": "metadata",
                    "conversation_id": self.conversation_id,
                    "start_time": datetime.now().isoformat(),
                    "model": self.model
                }
                f.write(json.dumps(metadata) + "\n")
    
    def _log_interaction(self, prompt: str, response_data: Any, success: bool = True, error: str = None,type:str = "agent"):
        """Log API interactions."""
        # self._init_log_file(type)
        
        log_entry = {
            "type": "interaction",
            "timestamp": datetime.now().isoformat(),
            "request_count": self.request_count,
            "success": success,
            "input": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        }
        
        if success and response_data:
            if isinstance(response_data, dict):
                log_entry["response"] = response_data
            elif hasattr(response_data, 'text'):
                try:
                    log_entry["response"] = json.loads(response_data.text)
                except json.JSONDecodeError:
                    log_entry["response"] = response_data.text
            else:
                log_entry["response"] = str(response_data)
        
        if error:
            log_entry["error"] = error
        
        # with open(self.log_file, "a", encoding="utf-8") as f:
        #     f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
