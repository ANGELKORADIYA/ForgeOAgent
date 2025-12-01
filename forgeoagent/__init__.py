from .clients import GeminiAPIClient
from .controller import create_master_executor
from .core import PyClassAnalyzer
from .config import config

from .main import main

import os
import atexit

SECURITY_ENABLED = os.getenv('SECURITY_ENABLED', 'False') == 'True' or os.getenv('SECURITY_ENABLED', 'False') == 'true' or os.getenv('SECURITY_ENABLED', 'False') == '1'
if SECURITY_ENABLED:
    from .core import SecurityManager
    security = SecurityManager()
    security.start_monitoring()
    atexit.register(security.stop_monitoring)  # Clean shutdown on exit