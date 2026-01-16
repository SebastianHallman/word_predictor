from __future__ import annotations

from pathlib import Path
from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from .config import MAX_SUGGESTIONS
from .storage import load_settings, save_settings
from .wordlists import build_sentence_starters, get_available_wordlist_files


class SettingsDialog(QtWidgets.QDialog):
    colors_changed = QtCore.Signal(str, str, bool)

    def __init__(
        self,
        *,
        available: list[Path],
        disabled: set[str],
        font_size: int,
        font_family: str,
        max_suggestions: int,
        text_color: str,
        bg_color: str,
        bg_transparent: bool,
        space_on_sentence_end: bool,
        parent: QtWidgets.QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)

        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(8, 36)
        self.size_spin.setValue(font_size)

        self.font_combo = QtWidgets.QFontComboBox()
        self.font_combo.setFontFilters(QtWidgets.QFontComboBox.FontFilter.MonospacedFonts)
        self.font_combo.setCurrentFont(QtGui.QFont(font_family))

        self.max_suggestions_spin = QtWidgets.QSpinBox()
        self.max_suggestions_spin.setRange(1, MAX_SUGGESTIONS)
        self.max_suggestions_spin.setValue(max_suggestions)

        self.text_color = text_color
        self.bg_color = bg_color
        self.bg_transparent = bg_transparent
        self.space_at_sentence_end = space_on_sentence_end

        self.text_color_swatch = self._color_swatch(self.text_color)
        self.bg_color_swatch = self._color_swatch(self.bg_color)
        self.bg_transparent_check = QtWidgets.QCheckBox("Transparent background")
        self.bg_transparent_check.setChecked(self.bg_transparent)

        self.space_at_sentence_end_check = QtWidgets.QCheckBox(
            "Automatically add space on sentence end (when pressing (.) (,) (?) (!))"
        )
        self.space_at_sentence_end_check.setChecked(self.space_at_sentence_end)

        self._checkboxes: list[tuple[str, QtWidgets.QCheckBox]] = []

        layout = QtWidgets.QVBoxLayout(self)

        prefs_group = QtWidgets.QGroupBox("Preferences")
        prefs_layout = QtWidgets.QFormLayout(prefs_group)
        prefs_layout.addRow("Font family", self.font_combo)
        prefs_layout.addRow("Font size", self.size_spin)
        prefs_layout.addRow("Max suggestions", self.max_suggestions_spin)
        prefs_layout.addRow("Text color", self.text_color_swatch)
        prefs_layout.addRow("Background color", self.bg_color_swatch)
        prefs_layout.addRow(self.bg_transparent_check)


        preview_group = QtWidgets.QGroupBox("Preview")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        self.preview_label = QtWidgets.QLabel("F1   quick\nF2   brown\nF3   fox\nF4   jumps\nF5   over")
        self.preview_label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.preview_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.preview_label.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.preview_label.setMargin(8)
        preview_layout.addWidget(self.preview_label)

        top_row = QtWidgets.QHBoxLayout()
        top_row.addWidget(prefs_group)
        top_row.addWidget(preview_group, 1)
        layout.addLayout(top_row)

        help_features = QtWidgets.QGroupBox("Extra features")
        help_layout = QtWidgets.QVBoxLayout(help_features)
        help_layout.addWidget(self.space_at_sentence_end_check)
        layout.addWidget(help_features)

        info = QtWidgets.QLabel("Choose which wordlists to use (from the wordlists/ folder):")
        info.setWordWrap(True)

        form = QtWidgets.QWidget()
        form_layout = QtWidgets.QVBoxLayout(form)
        form_layout.setContentsMargins(0, 0, 0, 0)

        if not available:
            empty = QtWidgets.QLabel("No .txt wordlists found in wordlists/.")
            form_layout.addWidget(empty)
        else:
            for path in available:
                cb = QtWidgets.QCheckBox(path.name)
                cb.setChecked(path.name not in disabled)
                form_layout.addWidget(cb)
                self._checkboxes.append((path.name, cb))

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)
        scroll.setMinimumWidth(360)

        select_all = QtWidgets.QPushButton("Select all")
        select_none = QtWidgets.QPushButton("Select none")
        select_all.clicked.connect(lambda: [cb.setChecked(True) for _, cb in self._checkboxes])
        select_none.clicked.connect(lambda: [cb.setChecked(False) for _, cb in self._checkboxes])

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(select_all)
        controls.addWidget(select_none)
        controls.addStretch(1)

        wordlists_group = QtWidgets.QGroupBox("Wordlists")
        wordlists_layout = QtWidgets.QVBoxLayout(wordlists_group)
        wordlists_layout.addWidget(info)
        wordlists_layout.addWidget(scroll, 1)
        wordlists_layout.addLayout(controls)
        layout.addWidget(wordlists_group, 1)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Save | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.text_color_swatch.clicked.connect(lambda: self._choose_color("Text color", True))
        self.bg_color_swatch.clicked.connect(lambda: self._choose_color("Background color", False))
        self.bg_transparent_check.toggled.connect(self._set_bg_transparent)

    def disabled_wordlists(self) -> list[str]:
        disabled: list[str] = []
        for name, cb in self._checkboxes:
            if not cb.isChecked():
                disabled.append(name)
        return disabled
    
    def font_size(self) -> int:
        return int(self.size_spin.value())

    def max_suggestions(self) -> int:
        return int(self.max_suggestions_spin.value())

    def font_family(self) -> str:
        return self.font_combo.currentFont().family()

    def update_preview(self) -> None:
        preview_bg = "transparent" if self.bg_transparent else self.bg_color
        self.preview_label.setFont(
            QtGui.QFont(self.font_combo.currentFont().family(), int(self.size_spin.value()))
        )
        self.preview_label.setStyleSheet(
            f"color: {self.text_color}; background-color: {preview_bg};"
        )

    def current_text_color(self) -> str:
        return self.text_color

    def current_bg_color(self) -> str:
        return self._normalize_bg_color(self.bg_color, self.bg_transparent)

    def current_bg_transparent(self) -> bool:
        return bool(self.bg_transparent)

    def space_on_sentence_end(self) -> bool:
        return bool(self.space_at_sentence_end_check.isChecked())

    def _choose_color(self, title: str, is_text: bool) -> None:
        initial = self.text_color if is_text else self.bg_color
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(initial),
            self,
            title,
            QtWidgets.QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if not color.isValid():
            return
        value = color.name(QtGui.QColor.NameFormat.HexArgb)
        if is_text:
            self.text_color = value
            self._update_swatch(self.text_color_swatch, value)
        else:
            self.bg_color = self._normalize_bg_color(value, self.bg_transparent)
            self._update_swatch(self.bg_color_swatch, value)
            if self.bg_transparent:
                self.bg_transparent = False
                self.bg_transparent_check.setChecked(False)
        self.update_preview()
        self.colors_changed.emit(self.text_color, self.bg_color, self.bg_transparent)

    def _color_swatch(self, color: str) -> "ColorSwatch":
        label = ColorSwatch(color)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        label.setMinimumWidth(120)
        self._update_swatch(label, color)
        return label

    def _update_swatch(self, label: QtWidgets.QLabel, color: str) -> None:
        label.setText(color)
        text_color = "#ffffffff" if QtGui.QColor(color).lightness() < 128 else "#ff000000"
        label.setStyleSheet(f"color: {text_color}; background-color: {color};")

    def _set_bg_transparent(self, checked: bool) -> None:
        self.bg_transparent = bool(checked)
        if not self.bg_transparent:
            self.bg_color = self._normalize_bg_color(self.bg_color, False)
        self.update_preview()
        self.colors_changed.emit(self.text_color, self.bg_color, self.bg_transparent)

    def _normalize_bg_color(self, color: str, transparent: bool) -> str:
        if transparent:
            return color
        qcolor = QtGui.QColor(color)
        qcolor.setAlpha(255)
        return qcolor.name(QtGui.QColor.NameFormat.HexArgb)


class ColorSwatch(QtWidgets.QLabel):
    clicked = QtCore.Signal()

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)



class Overlay(QtWidgets.QWidget):
    def __init__(
        self,
        state,
        *,
        font_size: int,
        font_family: str,
        text_color: str,
        bg_color: str,
        bg_transparent: bool,
        space_on_sentence_end: bool,
        request_rebuild=None,
    ):
        super().__init__()
        self._state = state
        self._auto_position = True
        self._moving_programmatically = False
        self._drag_active = False
        self._drag_moved = False
        self._drag_offset = QtCore.QPoint()
        self._drag_menu_action = False
        self._drag_press_pos = QtCore.QPoint()
        self.setObjectName("Overlay")
        self.setWindowTitle("Speedy writer")
        self._base_flags = QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(self._base_flags)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self.setAutoFillBackground(False)

        self._text_color = text_color
        self._bg_color = bg_color
        self._bg_transparent = bg_transparent
        self._space_on_sentence_end = bool(space_on_sentence_end)
        self._request_rebuild = request_rebuild
        self._apply_theme()

        self.menu_bar = QtWidgets.QMenuBar(self)
        self.menu_bar.setNativeMenuBar(False)
        self.menu = self.menu_bar.addMenu("Menu")
        menu = self.menu
        settings_action = menu.addAction("Settings…")
        quit_action = menu.addAction("Quit")
        settings_action.triggered.connect(self.open_settings)
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.menu_bar.installEventFilter(self)

        self.label = QtWidgets.QLabel()
        self.label.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        self._apply_font(font_size, font_family)

        

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setMenuBar(self.menu_bar)
        layout.addWidget(self.label)

        self._suggestions: List[str] = []

        self._margin = 20
        self.resize(420, 260)
        self.move_to_lower_right()
        self.show()

    def move_to_lower_right(self) -> None:
        if not self._auto_position:
            return
        screen = QtGui.QGuiApplication.primaryScreen()
        geo = screen.availableGeometry()
        x = geo.x() + geo.width() - self.width() - self._margin
        y = geo.y() + geo.height() - self.height() - self._margin
        self._moving_programmatically = True
        self.move(x, y)
        self._moving_programmatically = False

    def update_suggestions(self, suggestions: List[str], prefix: str) -> None:
        self._suggestions = suggestions
        if suggestions:
            lines = []
            for i, s in enumerate(suggestions, start=1):
                key = f"F{i}" if i < 10 else "F10"
                lines.append(f"{key:<4} {s}")
            text = "\n".join(lines)
        else:
            text = "No suggestions" if prefix else "Write something"

        self.label.setText(text)
        self.move_to_lower_right()

    def get_choice(self, idx_1_based: int) -> str | None:
        if 1 <= idx_1_based <= len(self._suggestions):
            return self._suggestions[idx_1_based - 1]
        return None

    def _apply_font(self, font_size: int, font_family: str) -> None:
        self.label.setFont(QtGui.QFont(font_family, int(font_size)))

    def _apply_theme(self) -> None:
        bg_color = "transparent" if self._bg_transparent else self._bg_color
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, self._bg_transparent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground, self._bg_transparent)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_OpaquePaintEvent, not self._bg_transparent)
        self.setAutoFillBackground(not self._bg_transparent)
        if self._bg_transparent:
            self.setWindowFlags(self._base_flags | QtCore.Qt.WindowType.FramelessWindowHint)
        else:
            self.setWindowFlags(self._base_flags)
        self.setStyleSheet(
            "#Overlay {"
            f"  background-color: {bg_color};"
            "  border: 1px solid rgba(255, 255, 255, 60);"
            "  border-radius: 10px;"
            "}"
            "QMenuBar {"
            "  background-color: rgba(20, 20, 20, 255);"
            "  color: white;"
            "  padding: 4px;"
            "}"
            "QMenuBar::item {"
            "  background: transparent;"
            "  padding: 4px 8px;"
            "}"
            "QMenuBar::item:selected {"
            "  background-color: rgba(255, 255, 255, 30);"
            "  border-radius: 6px;"
            "}"
            "QMenu {"
            "  background-color: rgba(30, 30, 30, 255);"
            "  color: white;"
            "  border: 1px solid rgba(255, 255, 255, 60);"
            "}"
            "QMenu::item:selected {"
            "  background-color: rgba(255, 255, 255, 40);"
            "}"
            f"QLabel {{ color: {self._text_color}; }}"
        )
        self.show()

    def moveEvent(self, event: QtGui.QMoveEvent) -> None:
        if not self._moving_programmatically:
            self._auto_position = False
        super().moveEvent(event)

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched is self.menu_bar and self._bg_transparent:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                mouse = QtGui.QMouseEvent(event)
                if mouse.button() == QtCore.Qt.MouseButton.LeftButton:
                    action = self.menu_bar.actionAt(mouse.position().toPoint())
                    self._drag_menu_action = action == self.menu.menuAction()
                    self._drag_active = True
                    self._drag_moved = False
                    self._drag_press_pos = mouse.globalPosition().toPoint()
                    self._drag_offset = mouse.globalPosition().toPoint() - self.frameGeometry().topLeft()
                    return True
            elif event.type() == QtCore.QEvent.Type.MouseMove and self._drag_active:
                mouse = QtGui.QMouseEvent(event)
                if mouse.buttons() & QtCore.Qt.MouseButton.LeftButton:
                    if not self._drag_moved:
                        distance = (mouse.globalPosition().toPoint() - self._drag_press_pos).manhattanLength()
                        if distance < QtWidgets.QApplication.startDragDistance():
                            return True
                        self._drag_moved = True
                    self.move(mouse.globalPosition().toPoint() - self._drag_offset)
                    return True
            elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._drag_active:
                mouse = QtGui.QMouseEvent(event)
                self._drag_active = False
                if self._drag_menu_action and not self._drag_moved and mouse.button() == QtCore.Qt.MouseButton.LeftButton:
                    action_rect = self.menu_bar.actionGeometry(self.menu.menuAction())
                    pos = self.menu_bar.mapToGlobal(action_rect.bottomLeft())
                    self.menu.popup(pos)
                return True
        return super().eventFilter(watched, event)

    def open_settings(self) -> None:
        settings = load_settings()
        current_disabled = (
            set(settings.get("disabled_wordlists", []))
            if isinstance(settings.get("disabled_wordlists", []), list)
            else set()
        )
        font_size = settings.get("font_size", 11)
        max_suggestions = settings.get("max_suggestions", MAX_SUGGESTIONS)
        font_family = settings.get("font_family", "Consolas")
        text_color = settings.get("text_color", "#ffffffff")
        bg_color = settings.get("bg_color", "#e61e1e1e")
        bg_transparent = settings.get("bg_transparent", False)
        space_on_sentence_end = settings.get("space_on_sentence_end", True)

        dlg = SettingsDialog(
            available=get_available_wordlist_files(),
            disabled=current_disabled,
            font_size=font_size,
            font_family=font_family,
            max_suggestions=max_suggestions,
            text_color=text_color,
            bg_color=bg_color,
            bg_transparent=bg_transparent,
            space_on_sentence_end=space_on_sentence_end,
            parent=self,
        )

        original_font_size = font_size
        original_font_family = font_family
        original_max_suggestions = max_suggestions
        original_text_color = text_color
        original_bg_color = bg_color
        original_bg_transparent = bg_transparent
        original_space_on_sentence_end = space_on_sentence_end

        dlg.size_spin.valueChanged.connect(
            lambda value: (
                self._apply_font(value, dlg.font_combo.currentFont().family()),
                dlg.update_preview(),
            )
        )
        dlg.font_combo.currentFontChanged.connect(
            lambda font: (
                self._apply_font(dlg.size_spin.value(), font.family()),
                dlg.update_preview(),
            )
        )
        dlg.max_suggestions_spin.valueChanged.connect(self._state.set_max_suggestions)
        dlg.rejected.connect(
            lambda: (
                self._apply_font(original_font_size, original_font_family),
                self._set_colors(original_text_color, original_bg_color, original_bg_transparent),
                self._set_space_on_sentence_end(original_space_on_sentence_end),
                self._state.set_max_suggestions(original_max_suggestions),
            )
        )
        dlg.update_preview()
        dlg.colors_changed.connect(self._set_colors)
        dlg.space_at_sentence_end_check.toggled.connect(self._set_space_on_sentence_end)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        settings["disabled_wordlists"] = dlg.disabled_wordlists()
        settings["font_size"] = dlg.font_size()
        settings["max_suggestions"] = dlg.max_suggestions()
        settings["font_family"] = dlg.font_family()
        settings["text_color"] = dlg.current_text_color()
        settings["bg_color"] = dlg.current_bg_color()
        settings["bg_transparent"] = dlg.current_bg_transparent()
        settings["space_on_sentence_end"] = dlg.space_on_sentence_end()
        save_settings(settings)

        new_size = settings["font_size"]
        new_max = settings["max_suggestions"]
        new_family = settings["font_family"]
        self._state.set_max_suggestions(new_max)
        if bg_transparent != settings["bg_transparent"] and self._request_rebuild:
            self._request_rebuild(settings)
            self.close()
        else:
            self._apply_font(new_size, new_family)
            self._set_colors(
                settings["text_color"],
                settings["bg_color"],
                settings["bg_transparent"],
            )
            self._set_space_on_sentence_end(settings["space_on_sentence_end"])

        disabled = set(settings["disabled_wordlists"])
        self._state.set_sentence_starters(build_sentence_starters(disabled))
        self._state.reload_wordlists(disabled_wordlists=disabled)

    def _set_colors(self, text_color: str, bg_color: str, bg_transparent: bool) -> None:
        self._text_color = text_color
        self._bg_color = bg_color
        self._bg_transparent = bg_transparent
        self._apply_theme()

    def _set_space_on_sentence_end(self, enabled: bool) -> None:
        self._space_on_sentence_end = bool(enabled)

    def space_on_sentence_end(self) -> bool:
        return self._space_on_sentence_end

    def contextMenuEvent(self, event: QtGui.QContextMenuEvent):
        menu = QtWidgets.QMenu(self)
        settings_action = menu.addAction("Settings…")
        quit_action = menu.addAction("Quit")

        chosen = menu.exec(event.globalPos())
        if chosen == settings_action:
            self.open_settings()
        elif chosen == quit_action:
            QtWidgets.QApplication.quit()
