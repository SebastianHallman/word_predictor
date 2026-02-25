# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python desktop app for word prediction.
- Entry point: `main.py` (imports and runs `speedy_writer.app.main`).
- Core package: `speedy_writer/`.
  - `app.py`: app bootstrap and wiring.
  - `predictor.py`: suggestion ranking logic.
  - `hooks.py`: keyboard hook integration.
  - `ui.py`: overlay window and settings UI.
  - `state.py`, `storage.py`, `wordlists.py`, `config.py`: shared state, persistence, list loading, constants.
- Dictionary data: `wordlists/` (`en.txt`, `sv.txt`; one word per line).

## Build, Test, and Development Commands
Use a virtual environment for local development.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install PySide6 keyboard
python main.py
```

- `python main.py`: runs the overlay app.
- `pip install PySide6 keyboard`: installs runtime dependencies described in `README.md`.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation.
- Keep modules and functions `snake_case`; classes `PascalCase`; constants `UPPER_SNAKE_CASE`.
- Preserve existing type-hint style (e.g., `list[str]`, `dict[str, int]`) and `from __future__ import annotations` where already used.
- Prefer small, focused functions in `speedy_writer/` and keep UI logic separate from predictor logic.

## Testing Guidelines
There is currently no formal test suite in this repository.
- For logic changes, add focused tests under a future `tests/` directory using `pytest`.
- Name test files `test_<module>.py` and test functions `test_<behavior>()`.
- For UI/hook changes, do a manual smoke test by running `python main.py` and validating suggestions, key selection (`F1`-`F10`), and settings persistence.

## Commit & Pull Request Guidelines
Current history uses short, imperative messages (for example, `README update`, `first commit`).
- Prefer concise commit titles in imperative mood, optionally scoped (example: `predictor: sort ties by length`).
- Keep commits focused on one change.
- PRs should include: summary, why the change is needed, manual test notes, and screenshots/GIFs for UI changes.
- Link related issues when available.

## Security & Configuration Tips
- Do not commit files from `.venv/` or user data from `~/.speedy_writer/`.
- Treat keyboard hooks carefully; some systems require elevated permissions for `keyboard`.
- Keep `EXTRA_WORDLIST_PATHS` in `speedy_writer/config.py` environment-specific and out of commits unless intentionally shared.
