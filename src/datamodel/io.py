from __future__ import annotations

import json
from typing import Any, Dict
import yaml


class DataLoadError(ValueError):
    pass


def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise DataLoadError(f"YAML file '{path}' must be a mapping")
    return data


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise DataLoadError(f"JSON file '{path}' must be a mapping")
    return data


def write_json(path: str, payload: Any) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
