"""
swiftnode/config.py
==================
Centralized config loading, saving, and Pydantic-based validation.
Config file stored at ~/.swiftnode/config.json
"""
import json
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


CONFIG_DIR = Path.home() / ".swiftnode"
CONFIG_FILE = CONFIG_DIR / "config.json"


# ── Pydantic Schema ───────────────────────────────────────────────────────────

class SwiftNodeSettings(BaseModel):
    """Validated SwiftNode configuration schema (v5)."""

    # Provider / LLM
    provider: str = "openai"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1/chat/completions"
    model: str = "gpt-4o-mini"

    # Agent behaviour
    max_tool_iterations: int = Field(default=40, ge=1, le=100)
    context_window_tokens: int = Field(default=65_536, ge=4096)
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    reasoning_effort: Optional[str] = None  # "low" | "medium" | "high"

    # Bot platforms
    telegram_token: str = ""
    owner_id: str = ""
    bot_platform: str = "Telegram"

    # Multi-device
    multi_device_enabled: bool = False
    multi_device_token: str = ""
    multi_device_port: int = 7799
    connected_devices: list[str] = Field(default_factory=list)

    class Config:
        extra = "allow"  # Accept legacy keys without breaking


# ── Raw JSON Helpers ──────────────────────────────────────────────────────────

def get_config_path() -> Path:
    """Returns the config file path, creating the directory if needed."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_FILE


def load_config() -> dict:
    """Loads the raw config dict from ~/.swiftnode/config.json"""
    path = get_config_path()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Legacy: check for config.json in CWD
    cwd_config = Path("config.json")
    if cwd_config.exists():
        with open(cwd_config, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_settings() -> SwiftNodeSettings:
    """Loads and validates config as a SwiftNodeSettings Pydantic model."""
    raw = load_config()
    return SwiftNodeSettings(**raw)


def save_config(config: dict) -> None:
    """Saves the config to ~/.swiftnode/config.json"""
    path = get_config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def config_exists() -> bool:
    """Returns True if a config file already exists."""
    return CONFIG_FILE.exists() or Path("config.json").exists()
