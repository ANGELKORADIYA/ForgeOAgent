from forgeoagent.approval.policy import ApprovalPolicy
from forgeoagent.approval.requests import ApprovalRequest

class ApprovalEvaluator:
    """Evaluates requested actions against the active approval policy."""
    def __init__(self, policy: ApprovalPolicy):
        self.policy = policy
        
    def requires_approval(self, action: dict) -> bool:
        # Default behavior: all file mods, shell, or code execs trigger approval
        return True
