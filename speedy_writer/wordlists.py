from __future__ import annotations

from pathlib import Path

from .config import WORDLIST_DIR

EN_STARTERS = [
    "the",
    "and",
    "i",
    "you",
    "we",
    "it",
    "this",
    "that",
    "there",
    "so",
    "but",
    "because",
    "however",
    "then",
    "also",
]

SV_STARTERS = [
    "jag",
    "du",
    "vi",
    "det",
    "den",
    "de",
    "detta",
    "där",
    "så",
    "men",
    "för",
    "om",
    "när",
    "också",
    "nu",
]


def get_available_wordlist_files() -> list[Path]:
    if not WORDLIST_DIR.exists():
        return []
    return sorted(WORDLIST_DIR.glob("*.txt"))


def load_words_from_files(paths: list[Path]) -> set[str]:
    words: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            word = line.strip()
            if word:
                words.add(word)
    return words


def build_sentence_starters(disabled_wordlists: set[str]) -> list[str]:
    enabled = [p.name.lower() for p in get_available_wordlist_files() if p.name not in disabled_wordlists]
    langs: set[str] = set()
    for name in enabled:
        if "sv" in name or "swedish" in name:
            langs.add("sv")
        if "en" in name or "english" in name:
            langs.add("en")
    if not langs:
        langs = {"en"}
    starters: list[str] = []
    if "sv" in langs:
        starters.extend(SV_STARTERS)
    if "en" in langs:
        starters.extend(EN_STARTERS)
    seen: set[str] = set()
    unique: list[str] = []
    for word in starters:
        if word not in seen:
            seen.add(word)
            if word:
                unique.append(word[0].upper() + word[1:])
    return unique
