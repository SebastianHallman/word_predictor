# Speedy Writer

Speedy Writer is a small desktop overlay that suggests word completions as you type.
It listens to global keyboard input, shows up to 10 suggestions in a floating window,
and lets you accept a suggestion with the function keys (F1-F10). It also learns
from your typing by increasing word frequency each time you commit a word.


## What it does
- Displays a compact always-on-top overlay with suggestions for the current prefix.
- Accepts suggestions with F1-F10 and inserts the chosen word into the active app.
- Loads words from built-in lists and text files in `wordlists/`.
- Lets you enable/disable wordlists from the Settings menu.
- Customizable appearance (font family/size, text and background colors, transparency).
- Configurable max suggestion count and auto-space after sentence-ending punctuation.
- Persists learned word frequencies in `~/.speedy_writer/freq.json`.

## Technology used
- Python 3
- PySide6 (Qt) for the overlay UI
- `keyboard` for global key hooks

## How to run
1) Create and activate a virtual environment (optional but recommended).
2) Install dependencies:
```bash
pip install PySide6 keyboard
```
3) Run the app:
```bash
python main.py
```

## Wordlists
- Wordlists live in `wordlists/` as `.txt` files (one word per line).
- Included wordlists: `en` uses the Linux words file; `sv` is sourced from https://runeberg.org/words/ss100.txt.

## Notes
- The overlay appears in the lower-right corner and stays on top; you can drag it when transparent.
- Settings are saved to `~/.speedy_writer/settings.json`.
- The `keyboard` package may require elevated permissions on some systems.
