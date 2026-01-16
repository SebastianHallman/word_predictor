from __future__ import annotations

import re
import threading
from typing import Callable

import keyboard
from PySide6 import QtCore

from .storage import save_freq

WORD_RE = re.compile(r"^[\wåäöÅÄÖ'-]+$")


class TypingState(QtCore.QObject):
    suggestions_changed = QtCore.Signal(list, str)

    def __init__(self, predictor, *, wordlist_loader: Callable[[set[str] | None], list[str]] | None = None):
        super().__init__()
        self.predictor = predictor
        self._wordlist_loader = wordlist_loader
        self.buffer = ""
        self.last_word = ""
        self._sentence_end = False
        self._sentence_starters: list[str] = []
        self._lock = threading.Lock()

    def reset(self) -> None:
        with self._lock:
            self.buffer = ""
            self._sentence_end = False
        self.suggestions_changed.emit([], "")

    def on_char(self, ch: str) -> None:
        with self._lock:
            self.buffer += ch
            self._sentence_end = False
            prefix = self.buffer
        self.suggestions_changed.emit(self.predictor.suggest(prefix), prefix)

    def on_backspace(self) -> None:
        with self._lock:
            if self.buffer == self.buffer[:-1]:
                self.buffer = self.last_word
                self.last_word = ""
            else: 
                self.buffer = self.buffer[:-1]
            prefix = self.buffer
        self._emit_suggestions(prefix)

    def commit_word(self) -> None:
        with self._lock:
            word = self.buffer
            self.last_word = word
            self.buffer = ""
        if WORD_RE.match(word or ""):
            self.predictor.bump(word)
            save_freq(self.predictor.freq)
        self.suggestions_changed.emit([], "")

    def choose(self, word: str) -> None:
        # Replace the current typed prefix in the active app with the chosen word.
        with self._lock:
            prefix = self.buffer
            prefix_len = len(prefix)
            self.buffer = ""            
            self._sentence_end = False
            
            

        out_word = word
        if prefix:
            if prefix.isupper():
                out_word = word.upper()
            elif prefix[0].isupper() and word and word[0].isalpha():
                out_word = word[0].upper() + word[1:]

        if prefix_len > 0:
            # Delete the prefix the user typed.
            keyboard.send("backspace", do_press=True, do_release=True)
            for _ in range(prefix_len - 1):
                keyboard.send("backspace")
        
        keyboard.write(out_word)
        keyboard.write(" ")  # Remove if you don't want auto-space.
        self.last_word = out_word

        self.predictor.bump(out_word)
        save_freq(self.predictor.freq)
        self.suggestions_changed.emit([], "")

    def reload_wordlists(self, *, disabled_wordlists: set[str] | None = None) -> None:
        if self._wordlist_loader is None:
            return
        self.predictor.set_words(self._wordlist_loader(disabled_wordlists))
        self.reset()

    def set_max_suggestions(self, max_suggestions: int) -> None:
        self.predictor.set_max_suggestions(max_suggestions)
        with self._lock:
            prefix = self.buffer
        self._emit_suggestions(prefix)

    def set_sentence_end(self, is_end: bool) -> None:
        with self._lock:
            self._sentence_end = bool(is_end)
            prefix = self.buffer
        self._emit_suggestions(prefix)

    def set_sentence_starters(self, starters: list[str]) -> None:
        with self._lock:
            self._sentence_starters = list(starters)

    def _emit_suggestions(self, prefix: str) -> None:
        if prefix:
            suggestions = self.predictor.suggest(prefix)
        elif self._sentence_end and self._sentence_starters:
            suggestions = self._sentence_starters[: self.predictor.max_suggestions]
        else:
            suggestions = []
        self.suggestions_changed.emit(suggestions, prefix)
