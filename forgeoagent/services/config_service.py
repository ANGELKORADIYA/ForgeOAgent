from forgeoagent.config.defaults import default_settings

class ConfigService:
    """Service to handle application configuration state."""
    
    @staticmethod
    def get_settings():
        return default_settings
