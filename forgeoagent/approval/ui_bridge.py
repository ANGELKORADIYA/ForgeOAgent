from forgeoagent.approval.requests import ApprovalRequest

class ApprovalUIBridge:
    """Bridge for the orchestration engine to ask the UI for an approval."""
    def request_approval(self, request: ApprovalRequest) -> bool:
        # Will be bound to the wxPython or new Launcher UI dialog
        pass
