from forgeoagent.core.models.run_state import RunCheckpoint

class CheckpointStore:
    """Persists and retrieves run checkpoints."""
    
    def persist_checkpoint(self, checkpoint: RunCheckpoint):
        pass
        
    def load_checkpoint(self, run_id: str) -> RunCheckpoint:
        pass
