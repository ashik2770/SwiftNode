"""
swiftnode/config.py
==================
Centralized config loading and saving.
Config file stored at ~/.swiftnode/config.json
"""
import json
import os
from pathlib import Path


CONFIG_DIR = Path.home() / ".swiftnode"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config_path() -> Path:
    """Returns the config file path, creating the directory if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_FILE


def load_config() -> dict:
    """Loads the config from ~/.swiftnode/config.json"""
    path = get_config_path()
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Legacy: check for config.json in CWD  
    cwd_config = Path("config.json")
    if cwd_config.exists():
        with open(cwd_config, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    """Saves the config to ~/.swiftnode/config.json"""
    path = get_config_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


def config_exists() -> bool:
    """Returns True if a config file already exists."""
    return CONFIG_FILE.exists() or Path("config.json").exists()
