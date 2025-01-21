from dataclasses import dataclass, asdict, field
from pathlib import Path
import json
import os
import keyring

KEYRING_SERVICE = "guakegpt"

@dataclass
class LLMSettings:
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 1000
    system_prompt: str = "You are a helpful AI assistant."

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'LLMSettings':
        # Handle model name migration for Anthropic models
        if data.get("provider") == "anthropic":
            model = data.get("model", "")
            if model == "claude-3-opus":
                data["model"] = "claude-3-opus-20240229"
            elif model == "claude-3-sonnet":
                data["model"] = "claude-3-sonnet-20240229"
            elif model == "claude-3-haiku":
                data["model"] = "claude-3-haiku-20240229"
        return cls(**data)

@dataclass
class Settings:
    width_percent: int = 80
    height_percent: int = 50
    hotkey: str = "F12"
    animation_duration: int = 250
    hide_on_focus_loss: bool = True
    llm: LLMSettings = field(default_factory=LLMSettings)

    @property
    def api_key(self) -> str:
        return keyring.get_password(KEYRING_SERVICE, self.llm.provider) or ""

    @api_key.setter
    def api_key(self, value: str) -> None:
        if value:
            keyring.set_password(KEYRING_SERVICE, self.llm.provider, value)
        else:
            try:
                keyring.delete_password(KEYRING_SERVICE, self.llm.provider)
            except keyring.errors.PasswordDeleteError:
                pass

    @classmethod
    def load(cls) -> 'Settings':
        config_dir = Path.home() / ".config" / "guakegpt"
        config_file = config_dir / "config.json"
        
        if not config_file.exists():
            return cls()
        
        try:
            with open(config_file) as f:
                data = json.load(f)
                if "llm" in data:
                    data["llm"] = LLMSettings.from_dict(data["llm"])
                return cls(**data)
        except Exception:
            return cls()

    def save(self):
        config_dir = Path.home() / ".config" / "guakegpt"
        config_file = config_dir / "config.json"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        
        data = asdict(self)
        data["llm"] = self.llm.to_dict()
        
        with open(config_file, "w") as f:
            json.dump(data, f, indent=4) 