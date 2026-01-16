from __future__ import annotations

from typing import List, Tuple

from .config import MAX_SUGGESTIONS


class Predictor:
    def __init__(self, words: List[str], freq: dict[str, int], *, max_suggestions: int = MAX_SUGGESTIONS):
        self.words = words
        self.freq = freq
        self.max_suggestions = max(1, min(int(max_suggestions), MAX_SUGGESTIONS))

    def set_words(self, words: List[str]) -> None:
        self.words = words

    def set_max_suggestions(self, max_suggestions: int) -> None:
        self.max_suggestions = max(1, min(int(max_suggestions), MAX_SUGGESTIONS))

    def bump(self, word: str) -> None:
        lowered = word.lower()
        if not lowered:
            return
        self.freq[lowered] = int(self.freq.get(lowered, 0)) + 1

    def suggest(self, prefix: str) -> List[str]:
        normalized = prefix.lower().strip()
        if not normalized:
            return []

        matches = [w for w in self.words if w.lower().startswith(normalized)]

        # Sort by learned frequency (desc), then shortest first, then alphabetical.
        def key(word: str) -> Tuple[int, int, str]:
            return (-int(self.freq.get(word.lower(), 0)), len(word), word.lower())

        matches.sort(key=key)
        return matches[:self.max_suggestions]
