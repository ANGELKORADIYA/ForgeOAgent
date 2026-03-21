from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

class RunState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    WAITING_FOR_TOOL = "waiting_for_tool"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    WAITING_FOR_USER_INPUT = "waiting_for_user_input"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class RunCheckpoint:
    run_id: str
    state: RunState
    current_step: str
    provider_name: str
    agent_name: str
    messages: List[Dict] = field(default_factory=list)
    planned_actions: List[Dict] = field(default_factory=list)
    pending_action: Optional[Dict] = None
    last_result: Optional[Dict] = None
