from __future__ import annotations

from PySide6 import QtWidgets

from .config import EXTRA_WORDLIST_PATHS, MAX_SUGGESTIONS
from .predictor import Predictor
from .state import TypingState
from .storage import load_freq, load_settings
from .ui import Overlay
from .hooks import install_hooks
from .wordlists import build_sentence_starters, get_available_wordlist_files, load_words_from_files


BUILTIN_WORDS = [
    # Swedish (mixed)
    "jag",
    "du",
    "och",
    "att",
    "det",
    "som",
    "är",
    "för",
    "med",
    "inte",
    "kan",
    "ska",
    "vill",
    "till",
    "från",
    "när",
    "var",
    "där",
    "här",
    "rapport",
    "projekt",
    "kth",
    "unity",
    "hjärna",
    "hörsel",
    "spasm",
    # English
    "the",
    "and",
    "to",
    "of",
    "in",
    "that",
    "is",
    "for",
    "with",
    "not",
    "can",
    "will",
    "want",
    "from",
    "when",
    "where",
    "here",
    "report",
    "project",
    "brain",
    "hearing",
    "unity",
]


def load_all_words(*, disabled_wordlists: set[str] | None = None) -> list[str]:
    disabled = disabled_wordlists or set()
    paths = [p for p in get_available_wordlist_files() if p.name not in disabled]
    paths.extend([p for p in EXTRA_WORDLIST_PATHS if p.exists()])
    words = set(BUILTIN_WORDS)
    words.update(load_words_from_files(paths))
    return sorted(words)


def main() -> None:
    freq = load_freq()
    settings = load_settings()
    disabled = (
        set(settings.get("disabled_wordlists", []))
        if isinstance(settings.get("disabled_wordlists", []), list)
        else set()
    )
    font_size = settings.get("font_size", 11)
    font_family = settings.get("font_family", "Consolas")
    max_suggestions = settings.get("max_suggestions", MAX_SUGGESTIONS)
    text_color = settings.get("text_color", "#ffffffff")
    bg_color = settings.get("bg_color", "#e61e1e1e")
    bg_transparent = settings.get("bg_transparent", False)
    space_on_sentence_end = settings.get("space_on_sentence_end", True)

    predictor = Predictor(load_all_words(disabled_wordlists=disabled), freq, max_suggestions=max_suggestions)

    app = QtWidgets.QApplication([])
    state = TypingState(predictor, wordlist_loader=lambda disabled_wordlists: load_all_words(disabled_wordlists=disabled_wordlists))
    state.set_sentence_starters(build_sentence_starters(disabled))

    overlay_holder = {"overlay": None}

    def set_overlay(new_overlay: Overlay) -> None:
        current = overlay_holder.get("overlay")
        if current is not None:
            try:
                state.suggestions_changed.disconnect(current.update_suggestions)
            except (TypeError, RuntimeError):
                pass
            current.close()
        overlay_holder["overlay"] = new_overlay
        state.suggestions_changed.connect(new_overlay.update_suggestions)

    def request_rebuild(new_settings: dict) -> None:
        new_overlay = Overlay(
            state,
            font_size=new_settings["font_size"],
            font_family=new_settings["font_family"],
            text_color=new_settings["text_color"],
            bg_color=new_settings["bg_color"],
            bg_transparent=new_settings["bg_transparent"],
            space_on_sentence_end=new_settings["space_on_sentence_end"],
            request_rebuild=request_rebuild,
        )
        set_overlay(new_overlay)

    overlay = Overlay(
        state,
        font_size=font_size,
        font_family=font_family,
        text_color=text_color,
        bg_color=bg_color,
        bg_transparent=bg_transparent,
        space_on_sentence_end=space_on_sentence_end,
        request_rebuild=request_rebuild,
    )
    set_overlay(overlay)
    state.set_sentence_end(True)
    install_hooks(state, overlay_holder)
    app.exec()
