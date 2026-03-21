import os
from pathlib import Path

def get_appdata_dir() -> Path:
    """Config paths pointing to Roaming APPDATA or ~/.config"""
    if os.name == 'nt':
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~/.config')
    path = Path(base) / 'ForgeOAgent'
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_localappdata_dir() -> Path:
    """Cache and log paths pointing to LOCALAPPDATA or ~/.cache"""
    if os.name == 'nt':
        base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    else:
        base = os.path.expanduser('~/.cache')
    path = Path(base) / 'ForgeOAgent'
    path.mkdir(parents=True, exist_ok=True)
    return path

CONFIG_DIR = get_appdata_dir()
CACHE_DIR = get_localappdata_dir()
LOGS_DIR = CACHE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)
