import os 
import sys 
import yaml 
from pathlib import Path
from .model import AureliaConfig

# Purpose of this config.py file is to store the configuration of Aurelia and mainly the preferences of the user when he uses the application.

# ---------------
# Path Management
# --------------- 

CONFIG_DIR = Path.home() / ".aurelia"
CONFIG_DIR.mkdir(parents = True,exist_ok=True)

CONFIG_PATH = CONFIG_DIR / "config.yaml"

# ----------------------------
# Load Configuration
# ----------------------------

def load_config() -> AureliaConfig:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            data = yaml.safe_load(f) or {} # Edge case instead of return None.
            return AureliaConfig(**data)
    else:
        return AureliaConfig()

# ----------------------------
# Save Configuration
# ----------------------------
## To write the changes the config.yaml file as per the user's wish.
def save_config(config: AureliaConfig):
    with open(CONFIG_PATH, "w") as f:
        # mode='json' ensures Enums and other types are converted to strings/plain types
        data = config.model_dump(mode='json')
        yaml.safe_dump(data, f, default_flow_style=False)
        
