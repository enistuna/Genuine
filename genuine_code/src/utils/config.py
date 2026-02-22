import yaml, os

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file is not found at {config_path}")
        
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
