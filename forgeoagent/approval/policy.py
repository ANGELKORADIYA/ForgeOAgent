from dataclasses import dataclass

@dataclass
class ApprovalPolicy:
    """Policy configuration defining what actions require explicit user approval."""
    require_code_approval: bool = True
    require_shell_approval: bool = True
    require_file_write_approval: bool = True
    require_network_mutation_approval: bool = True
    auto_allow_read_only_tools: bool = True
