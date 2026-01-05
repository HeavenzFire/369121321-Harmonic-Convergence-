import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Any

ARTIFACT_DIR = "artifacts"

def save_json(data: Dict[str, Any], filename: str) -> None:
    """Save data as JSON artifact"""
    path = os.path.join(ARTIFACT_DIR, "json", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)

def save_csv(data: List[Dict[str, Any]], filename: str, fieldnames: List[str]) -> None:
    """Save data as CSV artifact"""
    path = os.path.join(ARTIFACT_DIR, "csv", filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def timestamp() -> str:
    """Generate timestamp for run IDs"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def log_run_info(run_id: str, algorithm: str, benchmark: str, seed: int, **kwargs) -> None:
    """Log run metadata"""
    info = {
        "run_id": run_id,
        "algorithm": algorithm,
        "benchmark": benchmark,
        "seed": seed,
        "timestamp": timestamp(),
        **kwargs
    }
    save_json(info, f"{run_id}_info.json")