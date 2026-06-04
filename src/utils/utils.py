import yaml
from pathlib import Path


def load_yaml_config(path: str|Path)->dict:
    path =Path(path)
    with open(path,'r') as f:
        return yaml.safe_load(f)