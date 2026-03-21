from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional

class AppSettings(BaseModel):
    active_provider: str = "gemini"
    log_dir: Path = Field(default_factory=lambda: Path("logs"))
    prompt_dir: Path = Field(default_factory=lambda: Path("forgeoagent/config/prompts"))
    enable_code_execution: bool = True
    
    class Config:
        env_file = ".env"
