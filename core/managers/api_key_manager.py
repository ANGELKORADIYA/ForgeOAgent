import threading
from typing import Dict, List, Any
from datetime import datetime, date


class GlobalAPIKeyManager:
    """Singleton class for managing API keys with error handling and rotation."""
    _instance = None
    _api_keys: List[str] = []
    _current_index: int = 0
    _failed_keys: set = set()
    _lock = threading.Lock()
    _usage_stats = {}
    _last_reset_date: date = None
    
    def __new__(cls):
        """To Make Class Singleton"""
        if cls._instance is None:
            cls._instance = super(GlobalAPIKeyManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def initialize(cls, api_keys: List[str]):
        """Initialize the API key manager with validation."""
        if not api_keys:
            # raise ValueError("API keys list cannot be empty")
            return
        
        with cls._lock:
            cls._api_keys = api_keys.copy()
            cls._current_index = 0
            cls._failed_keys = set()
            cls._usage_stats = {key: {"requests": 0, "failures": 0} for key in api_keys}
            cls._last_reset_date = date.today()
    
    @classmethod
    def _check_and_reset_daily(cls):
        """Check if it's a new day and reset failed keys if needed."""
        current_date = date.today()
        
        # If it's a new day since last reset
        if cls._last_reset_date is None or current_date > cls._last_reset_date:
            # print(f"🔄 New day detected ({current_date}). Resetting failed API keys...")
            
            # Reset failed keys
            # failed_count = len(cls._failed_keys)
            cls._failed_keys.clear()
            
            # Reset usage stats for the new day
            for key in cls._usage_stats:
                cls._usage_stats[key]["requests"] = 0
                cls._usage_stats[key]["failures"] = 0
            
            # Update last reset date
            cls._last_reset_date = current_date
            
            # if failed_count > 0:
            #     print(f"✅ Reset {failed_count} failed API keys for new day")
    
    @classmethod
    def get_current_key(cls) -> str:
        """Get current API key with intelligent rotation."""
        with cls._lock:
            if not cls._api_keys:
                raise Exception("No API keys initialized")
            
            # Check and reset failed keys if it's a new day
            cls._check_and_reset_daily()
            
            # Find next available key
            attempts = 0
            start_index = cls._current_index
            
            while cls._api_keys[cls._current_index] in cls._failed_keys:
                cls._current_index = (cls._current_index + 1) % len(cls._api_keys)
                attempts += 1
                
                if attempts >= len(cls._api_keys):
                    raise Exception("All API keys have failed")
                    
                if cls._current_index == start_index:
                    break
            
            current_key = cls._api_keys[cls._current_index]
            cls._usage_stats[current_key]["requests"] += 1
            return current_key
    
    @classmethod
    def mark_key_failed(cls, api_key: str, error_msg: str = ""):
        """Mark an API key as failed with error tracking."""
        with cls._lock:
            # Check and reset failed keys if it's a new day
            cls._check_and_reset_daily()
            
            cls._failed_keys.add(api_key)
            if api_key in cls._usage_stats:
                cls._usage_stats[api_key]["failures"] += 1
            # print(f"🔥 API Key marked as failed: {api_key[:10]}... | Error: {error_msg}")
    
    @classmethod
    def force_reset_failed_keys(cls):
        """Manually reset all failed keys (useful for testing or manual intervention)."""
        with cls._lock:
            # failed_count = len(cls._failed_keys)
            cls._failed_keys.clear()
            cls._last_reset_date = date.today()
            # print(f"🔄 Manually reset {failed_count} failed API keys")
    
    @classmethod
    def get_detailed_status(cls) -> Dict[str, Any]:
        """Get comprehensive status information."""
        with cls._lock:
            # Check and reset failed keys if it's a new day
            cls._check_and_reset_daily()
            
            return {
                'total_keys': len(cls._api_keys),
                'active_keys': len(cls._api_keys) - len(cls._failed_keys),
                'failed_keys': len(cls._failed_keys),
                'current_index': cls._current_index,
                'current_key_prefix': cls._api_keys[cls._current_index][:10] + "..." if cls._api_keys else "None",
                'usage_stats': cls._usage_stats.copy(),
                'last_reset_date': cls._last_reset_date.strftime('%Y-%m-%d') if cls._last_reset_date else None,
                'current_date': date.today().strftime('%Y-%m-%d')
            }