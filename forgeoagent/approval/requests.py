from dataclasses import dataclass
from typing import Optional

@dataclass
class ApprovalRequest:
    """Payload representing an action requiring user approval."""
    run_id: str
    action_type: str
    title: str
    summary: str
    risk_level: str
    preview: str
    diff: Optional[str] = None
    command: Optional[str] = None
    generated_code: Optional[str] = None
