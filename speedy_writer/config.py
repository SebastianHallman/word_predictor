from __future__ import annotations

from pathlib import Path

MAX_SUGGESTIONS = 10

# Persist user data in the home directory.
DATA_DIR = Path.home() / ".speedy_writer"
FREQ_PATH = DATA_DIR / "freq.json"
SETTINGS_PATH = DATA_DIR / "settings.json"

# Project-local wordlists live next to main.py in ./wordlists.
PROJECT_DIR = Path(__file__).resolve().parents[1]
WORDLIST_DIR = PROJECT_DIR / "wordlists"

# Optional extra wordlists (one file per entry) if you want to load lists outside ./wordlists.
EXTRA_WORDLIST_PATHS: list[Path] = []
