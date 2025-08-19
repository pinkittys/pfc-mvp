import os, csv, json
from typing import List, Dict, Any

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

def _read_csv(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def load_flowers() -> List[Dict[str, Any]]:
    return _read_csv(os.path.join(DATA_DIR, "flowers.csv"))

def load_templates() -> List[Dict[str, Any]]:
    return _read_csv(os.path.join(DATA_DIR, "templates.csv"))

def load_images_index() -> List[Dict[str, Any]]:
    return _read_csv(os.path.join(DATA_DIR, "images_index.csv"))

def load_rules() -> Dict[str, Any]:
    path = os.path.join(DATA_DIR, "rules.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)
