from dataclasses import dataclass
from pathlib import Path
import json
import os

@dataclass
class Settings:
    width_percent: int = 80
    height_percent: int = 50
    hotkey: str = "F12"
    animation_duration: int = 250
    hide_on_focus_loss: bool = True

    @classmethod
    def load(cls) -> 'Settings':
        config_dir = Path.home() / ".config" / "guakegpt"
        config_file = config_dir / "config.json"
        
        if not config_file.exists():
            return cls()
        
        try:
            with open(config_file) as f:
                data = json.load(f)
            return cls(**data)
        except Exception:
            return cls()

    def save(self):
        config_dir = Path.home() / ".config" / "guakegpt"
        config_file = config_dir / "config.json"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, "w") as f:
            json.dump(self.__dict__, f, indent=4) 