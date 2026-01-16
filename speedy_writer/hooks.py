from __future__ import annotations

import keyboard


def install_hooks(state, overlay_holder) -> None:
    # Register function keys as hotkeys with suppress=True so they don't propagate to other apps.
    for idx in range(1, 11):
        key = f"f{idx}"

        def on_fkey(_e: keyboard.KeyboardEvent, idx=idx):
            overlay = overlay_holder.get("overlay")
            if overlay is None:
                return
            choice = overlay.get_choice(idx)
            if choice:
                state.choose(choice)

        keyboard.on_press_key(key, on_fkey, suppress=True)

    def on_event(e: keyboard.KeyboardEvent):
        if e.event_type != "down":
            return

        name = e.name

        # Function keys are handled above so we can suppress them.
        if name in [f"f{i}" for i in range(1, 11)]:
            return

        # Navigation keys: reset buffer to avoid desync.
        if name in ["left", "right", "up", "down", "home", "end", "page up", "page down", "esc"]:
            state.reset()
            state.set_sentence_end(False)
            return

        if name == "backspace":
            state.on_backspace()
            return

        # Commit on whitespace/punctuation.
        if name in ["space", "enter", "tab", ".", ",", ";", ":", "!", "?", "(", ")", "[", "]", "{", "}", "\"", "'"]:
            state.commit_word()
            
            if name in [".", "!", "?"]:
                state.set_sentence_end(True)
                overlay = overlay_holder.get("overlay")
                if overlay and overlay.space_on_sentence_end():
                    keyboard.send(" ")
            else:
                state.set_sentence_end(False)
            return

        # Ignore modifiers.
        if name in [
            "ctrl",
            "left ctrl",
            "right ctrl",
            "alt",
            "left alt",
            "right alt",
            "shift",
            "left shift",
            "right shift",
            "windows",
            "left windows",
            "right windows",
        ]:
            return

        # If ctrl/alt is pressed: reset to avoid desync from shortcuts.
        if keyboard.is_pressed("ctrl") or keyboard.is_pressed("alt"):
            state.reset()
            state.set_sentence_end(False)
            return

        # Normal character input: 'a', 'å', '1', etc.
        if isinstance(name, str) and len(name) == 1:
            state.on_char(name)
            return

    keyboard.hook(on_event, suppress=False)
