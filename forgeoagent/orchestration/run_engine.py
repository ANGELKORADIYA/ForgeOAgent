from forgeoagent.core.models.run_state import RunState, RunCheckpoint
from typing import Any

class RunEngine:
    """Engine responsible for executing the RunState machine."""
    def __init__(self, provider: Any, planner: Any, router: Any):
        self.provider = provider
        self.planner = planner
        self.router = router

    def next_step(self, run: RunCheckpoint) -> Any:
        """Executes a single step in the state machine until blocked by a tool/approval."""
        if run.state in [RunState.COMPLETED, RunState.FAILED, RunState.CANCELLED]:
            return None

        # Logic for breaking iteration would go here
        # E.g., request = self.planner.parse(self.provider.chat(...))
        pass
