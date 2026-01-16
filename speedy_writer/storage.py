from __future__ import annotations

import json
from typing import Any

from .config import DATA_DIR, FREQ_PATH, SETTINGS_PATH


def load_freq() -> dict[str, int]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if FREQ_PATH.exists():
        try:
            data = json.loads(FREQ_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def save_freq(freq: dict[str, int]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FREQ_PATH.write_text(json.dumps(freq, ensure_ascii=False, indent=2), encoding="utf-8")


def load_settings() -> dict[str, Any]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def save_settings(settings: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding="utf-8")

