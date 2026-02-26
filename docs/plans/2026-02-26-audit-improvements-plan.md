# Media Downloader Audit & Improvements - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor Media Downloader v2.0.0 to improve architecture, security, UI/UX, and backend quality.

**Architecture:** Split monolithic main_window.py (1430 lines) into focused widgets. Centralize styles. Secure credential storage with keyring. Add cancel support, SSH progress, Whisper model selector. Formal logging throughout.

**Tech Stack:** Python 3.8+, PySide6, yt-dlp, paramiko, keyring, logging

---

### Task 1: Create centralized styles module

**Files:**
- Create: `ui/widgets/__init__.py`
- Create: `ui/widgets/styles.py`

**Step 1: Create the widgets package**

Create `ui/widgets/__init__.py`:
```python
```

**Step 2: Create styles.py with all QSS**

Create `ui/widgets/styles.py` extracting all styles from `main_window.py:86-317` and `ssh_browser.py:45-131` into reusable functions:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Centralized QSS styles for the Matrix theme."""

from config import MATRIX_COLORS

_mc = MATRIX_COLORS


def app_stylesheet() -> str:
    """Main application stylesheet applied to QMainWindow."""
    return f"""
        QMainWindow {{
            background-color: {_mc['background']};
            color: {_mc['text']};
        }}
        QWidget {{
            background-color: {_mc['background']};
            color: {_mc['text']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 15px;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px;
            color: {_mc['accent']};
            font-weight: bold;
        }}
        QLineEdit {{
            padding: 10px;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
            selection-background-color: {_mc['accent_dark']};
            selection-color: {_mc['text_bright']};
        }}
        QLineEdit:focus {{
            border: 1px solid {_mc['accent']};
            background-color: {_mc['background_tertiary']};
        }}
        QLineEdit::placeholder {{
            color: {_mc['text_dim']};
        }}
        QPushButton {{
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11pt;
            background-color: {_mc['background_tertiary']};
            color: {_mc['text']};
            border: 1px solid {_mc['border_dim']};
        }}
        QPushButton:hover {{
            background-color: {_mc['accent_dark']};
            border: 1px solid {_mc['accent']};
            color: {_mc['text_bright']};
        }}
        QPushButton:pressed {{
            background-color: {_mc['background_secondary']};
        }}
        QPushButton:disabled {{
            background-color: {_mc['background']};
            color: {_mc['border_dim']};
            border: 1px solid {_mc['background_tertiary']};
        }}
        QComboBox {{
            padding: 10px;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
        }}
        QComboBox:hover {{
            border: 1px solid {_mc['accent']};
        }}
        QComboBox:focus {{
            border: 1px solid {_mc['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
            background-color: {_mc['background_tertiary']};
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {_mc['text']};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
            selection-background-color: {_mc['accent_dark']};
            selection-color: {_mc['text_bright']};
            border: 1px solid {_mc['border_dim']};
            outline: none;
        }}
        QProgressBar {{
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            text-align: center;
            height: 28px;
            font-weight: bold;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
        }}
        QProgressBar::chunk {{
            background-color: {_mc['accent']};
            border-radius: 3px;
        }}
        QTextEdit {{
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            background-color: {_mc['background']};
            color: {_mc['text']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            selection-background-color: {_mc['accent_dark']};
            selection-color: {_mc['text_bright']};
            padding: 8px;
        }}
        QRadioButton {{
            font-size: 11pt;
            padding: 5px;
            color: {_mc['text']};
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid {_mc['border_dim']};
            background-color: {_mc['background_secondary']};
        }}
        QRadioButton::indicator:checked {{
            background-color: {_mc['accent']};
            border: 2px solid {_mc['accent']};
        }}
        QRadioButton::indicator:hover {{
            border: 2px solid {_mc['accent']};
        }}
        QLabel {{
            font-size: 11pt;
            color: {_mc['text']};
        }}
        QTabWidget::pane {{
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            background-color: {_mc['background_secondary']};
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['text_dim']};
            padding: 12px 24px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            border: 1px solid {_mc['border_dim']};
            border-bottom: none;
        }}
        QTabBar::tab:selected {{
            background-color: {_mc['background_secondary']};
            border-bottom: 2px solid {_mc['accent']};
            color: {_mc['accent']};
        }}
        QTabBar::tab:hover {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
        }}
        QScrollArea {{
            border: none;
            background-color: {_mc['background']};
        }}
        QScrollBar:vertical {{
            border: none;
            background-color: {_mc['background_secondary']};
            width: 10px;
            margin: 0;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {_mc['accent_dark']};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {_mc['accent']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background-color: {_mc['background_secondary']};
            height: 10px;
            margin: 0;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {_mc['accent_dark']};
            border-radius: 5px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {_mc['accent']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QCheckBox {{
            font-size: 11pt;
            color: {_mc['text']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 2px solid {_mc['border_dim']};
            background-color: {_mc['background_secondary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {_mc['accent']};
            border: 2px solid {_mc['accent']};
        }}
        QCheckBox::indicator:hover {{
            border: 2px solid {_mc['accent']};
        }}
    """


def download_button_style() -> str:
    """Style for the main download button with glow effect."""
    return f"""
        QPushButton {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
            font-weight: bold;
            padding: 14px 40px;
            font-size: 13pt;
            border: 2px solid {_mc['accent']};
            font-family: 'Consolas', monospace;
        }}
        QPushButton:hover {{
            background-color: {_mc['accent']};
            color: {_mc['background']};
            border: 2px solid {_mc['text_bright']};
        }}
        QPushButton:disabled {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['border_dim']};
            border: 2px solid {_mc['border_dim']};
        }}
    """


def cancel_button_style() -> str:
    """Style for the cancel button."""
    return f"""
        QPushButton {{
            background-color: #330011;
            color: {_mc['error']};
            font-weight: bold;
            padding: 14px 40px;
            font-size: 13pt;
            border: 2px solid {_mc['error']};
            font-family: 'Consolas', monospace;
        }}
        QPushButton:hover {{
            background-color: {_mc['error']};
            color: {_mc['background']};
            border: 2px solid #FF3366;
        }}
    """


def action_button_style(color_key: str) -> str:
    """Style for action buttons (info, warning, error variants)."""
    color = _mc.get(color_key, _mc['text'])
    hover_bg = {
        'info': '#003344',
        'warning': '#332200',
        'error': '#330011',
    }.get(color_key, _mc['background_tertiary'])
    return f"""
        QPushButton {{
            background-color: {_mc['background_tertiary']};
            color: {color};
            border: 1px solid {color};
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
            color: {color};
            border: 1px solid {color};
        }}
    """


def save_button_style() -> str:
    """Style for save/confirm buttons."""
    return f"""
        QPushButton {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
            border: 1px solid {_mc['accent']};
        }}
        QPushButton:hover {{
            background-color: {_mc['accent']};
            color: {_mc['background']};
        }}
    """


def select_button_style() -> str:
    """Style for SSH browser select button."""
    return f"""
        QPushButton {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
            font-weight: bold;
            padding: 12px 20px;
            border: 2px solid {_mc['accent']};
        }}
        QPushButton:hover {{
            background-color: {_mc['accent']};
            color: {_mc['background']};
        }}
        QPushButton:disabled {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['border_dim']};
            border: 2px solid {_mc['border_dim']};
        }}
    """


def dialog_stylesheet() -> str:
    """Stylesheet for dialogs (SSH browser, etc.)."""
    return f"""
        QDialog {{
            background-color: {_mc['background']};
            color: {_mc['text']};
        }}
        QLineEdit {{
            padding: 10px;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        QLineEdit:focus {{
            border: 1px solid {_mc['accent']};
            background-color: {_mc['background_tertiary']};
        }}
        QPushButton {{
            padding: 10px 18px;
            border-radius: 4px;
            font-weight: bold;
            background-color: {_mc['background_tertiary']};
            color: {_mc['text']};
            border: 1px solid {_mc['border_dim']};
            font-family: 'Consolas', monospace;
        }}
        QPushButton:hover {{
            background-color: {_mc['accent_dark']};
            border: 1px solid {_mc['accent']};
            color: {_mc['text_bright']};
        }}
        QPushButton:pressed {{
            background-color: {_mc['background_secondary']};
        }}
        QTreeWidget {{
            background-color: {_mc['background']};
            color: {_mc['text']};
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        QTreeWidget::item {{
            padding: 6px;
        }}
        QTreeWidget::item:selected {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
        }}
        QTreeWidget::item:hover {{
            background-color: {_mc['background_tertiary']};
        }}
        QTreeWidget::branch {{
            background-color: {_mc['background']};
        }}
        QHeaderView::section {{
            background-color: {_mc['background_secondary']};
            color: {_mc['accent']};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {_mc['border_dim']};
            font-weight: bold;
        }}
        QLabel {{
            color: {_mc['text']};
            font-size: 11pt;
            font-family: 'Consolas', monospace;
        }}
        QScrollBar:vertical {{
            border: none;
            background-color: {_mc['background_secondary']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {_mc['accent_dark']};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {_mc['accent']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def valid_field_style() -> str:
    """Style for validated input fields (valid)."""
    return f"border: 1px solid {_mc['success']};"


def invalid_field_style() -> str:
    """Style for validated input fields (invalid)."""
    return f"border: 1px solid {_mc['error']};"


def neutral_field_style() -> str:
    """Style for input fields with no validation state."""
    return f"border: 1px solid {_mc['border_dim']};"
```

**Step 3: Commit**

```bash
git add ui/widgets/__init__.py ui/widgets/styles.py
git commit -m "refactor: extract centralized QSS styles to ui/widgets/styles.py"
```

---

### Task 2: Create source_widget.py (Platform + URL)

**Files:**
- Create: `ui/widgets/source_widget.py`

**Step 1: Create source widget**

Create `ui/widgets/source_widget.py` extracting lines 356-394 from `main_window.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget for platform selection and URL input."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QGroupBox
)
from PySide6.QtCore import Signal

from config import SUPPORTED_PLATFORMS, MATRIX_COLORS
from utils.validators import InputValidator


class SourceWidget(QWidget):
    """Platform selector + URL input with auto-detection."""

    url_changed = Signal(str)
    platform_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        source_group = QGroupBox(">> FUENTE")
        source_layout = QVBoxLayout()
        source_layout.setSpacing(12)

        # Platform selector
        platform_layout = QHBoxLayout()
        platform_label = QLabel("Plataforma:")
        platform_label.setMinimumWidth(90)
        self.platform_combo = QComboBox()

        for platform_name, platform_info in SUPPORTED_PLATFORMS.items():
            icon = platform_info.get("icon", "")
            self.platform_combo.addItem(f"{icon} {platform_name}", platform_name)

        self.platform_combo.currentIndexChanged.connect(self._on_platform_changed)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_combo, 1)
        source_layout.addLayout(platform_layout)

        # URL field
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        url_label.setMinimumWidth(90)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pega aqui la URL del contenido...")
        self.url_input.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        source_layout.addLayout(url_layout)

        # Detected platform label
        self.detected_label = QLabel("")
        self.detected_label.setStyleSheet(
            f"color: {MATRIX_COLORS['text_dim']}; font-size: 9pt; padding-left: 95px;"
        )
        source_layout.addWidget(self.detected_label)

        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        self.setLayout(layout)

    def _on_url_changed(self, text):
        text = text.strip()
        if text:
            detected = InputValidator.detect_platform(text)
            if detected:
                self.detected_label.setText(f"Detectado: {detected}")
                for i in range(self.platform_combo.count()):
                    if self.platform_combo.itemData(i) == detected:
                        self.platform_combo.setCurrentIndex(i)
                        break
        else:
            self.detected_label.setText("")
        self.url_changed.emit(text)

    def _on_platform_changed(self, index):
        platform = self.platform_combo.currentData()
        if platform:
            self.platform_changed.emit(platform)

    def get_url(self) -> str:
        return self.url_input.text().strip()

    def get_platform(self) -> str:
        return self.platform_combo.currentData()

    def set_url_valid(self, valid: bool):
        """Apply visual validation feedback to URL field."""
        from ui.widgets.styles import valid_field_style, invalid_field_style, neutral_field_style
        if not self.url_input.text().strip():
            self.url_input.setStyleSheet(neutral_field_style())
        elif valid:
            self.url_input.setStyleSheet(valid_field_style())
        else:
            self.url_input.setStyleSheet(invalid_field_style())
```

**Step 2: Commit**

```bash
git add ui/widgets/source_widget.py
git commit -m "refactor: extract SourceWidget (platform + URL) from main_window"
```

---

### Task 3: Create options_widget.py (Format + Quality + Transcription)

**Files:**
- Create: `ui/widgets/options_widget.py`

**Step 1: Create options widget**

Create `ui/widgets/options_widget.py` extracting lines 396-454 from `main_window.py`, adding Whisper model selector:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget for download format, quality, and transcription options."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QGroupBox, QRadioButton, QCheckBox
)
from PySide6.QtCore import Signal

from config import VIDEO_QUALITIES, SUPPORTED_PLATFORMS, MATRIX_COLORS
from download.transcriber import AudioTranscriber


class OptionsWidget(QWidget):
    """Format, quality, and transcription options."""

    format_changed = Signal(bool)  # True = audio

    def __init__(self, default_format: str = "audio", parent=None):
        super().__init__(parent)
        self._init_ui(default_format)

    def _init_ui(self, default_format: str):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        options_group = QGroupBox(">> OPCIONES")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)

        # Format
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        format_label.setMinimumWidth(90)
        self.format_video = QRadioButton("Video (MP4)")
        self.format_audio = QRadioButton("Audio (MP3)")

        if default_format == "audio":
            self.format_audio.setChecked(True)
        else:
            self.format_video.setChecked(True)

        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_video)
        format_layout.addWidget(self.format_audio)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)

        # Quality (video only)
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Calidad:")
        quality_label.setMinimumWidth(90)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(VIDEO_QUALITIES)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo, 1)
        quality_layout.addStretch(2)
        options_layout.addLayout(quality_layout)

        # Transcription
        transcription_layout = QHBoxLayout()
        transcription_label = QLabel("Extra:")
        transcription_label.setMinimumWidth(90)
        self.transcription_checkbox = QCheckBox("Generar transcripcion (TXT)")
        self.transcription_checkbox.setToolTip(
            "Genera un archivo de texto con la transcripcion del audio usando IA"
        )
        self.transcription_checkbox.setEnabled(self.format_audio.isChecked())
        transcription_layout.addWidget(transcription_label)
        transcription_layout.addWidget(self.transcription_checkbox)
        transcription_layout.addStretch()
        options_layout.addLayout(transcription_layout)

        # Whisper model selector
        model_layout = QHBoxLayout()
        model_label = QLabel("Modelo IA:")
        model_label.setMinimumWidth(90)
        self.model_combo = QComboBox()
        model_info = AudioTranscriber.get_model_info()
        for name, info in model_info.items():
            self.model_combo.addItem(
                f"{name} ({info['size']} - {info['quality']})", name
            )
        self.model_combo.setCurrentIndex(1)  # default: base
        self.model_combo.setEnabled(False)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo, 1)
        model_layout.addStretch(2)
        options_layout.addLayout(model_layout)

        # Info labels
        self.capabilities_label = QLabel("")
        self.capabilities_label.setStyleSheet(
            f"color: {MATRIX_COLORS['warning']}; font-size: 9pt; padding-left: 95px;"
        )
        options_layout.addWidget(self.capabilities_label)

        self.transcription_info_label = QLabel("")
        self.transcription_info_label.setStyleSheet(
            f"color: {MATRIX_COLORS['info']}; font-size: 9pt; padding-left: 95px;"
        )
        options_layout.addWidget(self.transcription_info_label)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        self.setLayout(layout)

        # Connect signals
        self.format_video.toggled.connect(self._on_format_changed)
        self.format_audio.toggled.connect(self._on_format_changed)
        self.transcription_checkbox.toggled.connect(self._on_transcription_changed)

    def _on_format_changed(self):
        is_video = self.format_video.isChecked()
        is_audio = self.format_audio.isChecked()

        self.quality_combo.setEnabled(is_video)
        self.transcription_checkbox.setEnabled(is_audio)
        self.model_combo.setEnabled(is_audio and self.transcription_checkbox.isChecked())

        if is_video:
            self.transcription_checkbox.setChecked(False)
            self.transcription_info_label.setText("")
        else:
            self.transcription_info_label.setText(
                "La transcripcion usa Whisper AI (puede tardar)"
            )

        self.format_changed.emit(is_audio)

    def _on_transcription_changed(self, checked):
        self.model_combo.setEnabled(checked and self.format_audio.isChecked())

    def update_platform_capabilities(self, platform: str):
        """Update format options based on platform capabilities."""
        if platform not in SUPPORTED_PLATFORMS:
            return
        caps = SUPPORTED_PLATFORMS[platform]

        if not caps["supports_video"]:
            self.format_audio.setChecked(True)
            self.format_video.setEnabled(False)
            self.quality_combo.setEnabled(False)
            self.capabilities_label.setText("Esta plataforma solo soporta audio")
        elif not caps["supports_audio"]:
            self.format_video.setChecked(True)
            self.format_audio.setEnabled(False)
            self.quality_combo.setEnabled(True)
            self.capabilities_label.setText("Esta plataforma solo soporta video")
        else:
            self.format_video.setEnabled(True)
            self.format_audio.setEnabled(True)
            self.quality_combo.setEnabled(self.format_video.isChecked())
            self.capabilities_label.setText("")

    def is_audio(self) -> bool:
        return self.format_audio.isChecked()

    def get_quality(self) -> str:
        return self.quality_combo.currentText()

    def should_transcribe(self) -> bool:
        return self.transcription_checkbox.isChecked() and self.format_audio.isChecked()

    def get_whisper_model(self) -> str:
        return self.model_combo.currentData()
```

**Step 2: Commit**

```bash
git add ui/widgets/options_widget.py
git commit -m "refactor: extract OptionsWidget with Whisper model selector"
```

---

### Task 4: Create local_tab.py

**Files:**
- Create: `ui/widgets/local_tab.py`

**Step 1: Create local tab widget**

Create `ui/widgets/local_tab.py` extracting lines 459-486 from `main_window.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget for local download destination tab."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFileDialog
)
from PySide6.QtCore import Signal

from config import DEFAULT_DOWNLOAD_FOLDER
from utils.app_settings import AppSettings


class LocalTab(QWidget):
    """Local download folder selection tab."""

    folder_changed = Signal(str)

    def __init__(self, app_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.app_settings = app_settings
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        folder_group = QGroupBox(">> CARPETA LOCAL")
        folder_layout = QHBoxLayout()
        folder_layout.setContentsMargins(10, 10, 10, 10)

        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Selecciona la carpeta donde guardar el archivo...")
        last_folder = self.app_settings.get_last_local_folder()
        self.folder_input.setText(last_folder or DEFAULT_DOWNLOAD_FOLDER)
        self.folder_input.editingFinished.connect(self._save_folder)

        folder_button = QPushButton("Buscar...")
        folder_button.clicked.connect(self._select_folder)

        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_button)

        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)
        layout.addStretch()
        self.setLayout(layout)

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta de Destino", self.folder_input.text()
        )
        if folder:
            self.folder_input.setText(folder)
            self.app_settings.set_last_local_folder(folder)
            self.folder_changed.emit(folder)

    def _save_folder(self):
        folder = self.folder_input.text().strip()
        if folder:
            self.app_settings.set_last_local_folder(folder)
            self.folder_changed.emit(folder)

    def get_folder(self) -> str:
        return self.folder_input.text().strip()
```

**Step 2: Commit**

```bash
git add ui/widgets/local_tab.py
git commit -m "refactor: extract LocalTab widget from main_window"
```

---

### Task 5: Create ssh_tab.py

**Files:**
- Create: `ui/widgets/ssh_tab.py`

**Step 1: Create SSH tab widget**

Create `ui/widgets/ssh_tab.py` extracting lines 488-964 from `main_window.py`. This is the largest widget. It contains all SSH configuration, saved configs, connection testing, and folder browsing. See the full implementation — it extracts all the SSH-related methods (`load_saved_ssh_configs`, `load_ssh_config`, `save_current_ssh_config`, `clear_ssh_fields`, `test_ssh_connection`, `browse_ssh_folder`, `validate_ssh_inputs`, `get_ssh_config_dict`) from `main_window.py`.

Key signals: `message` (str, str) for log messages, `connection_tested` (bool) for connection status.

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget for SSH server configuration tab."""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QComboBox, QFormLayout, QFileDialog,
    QMessageBox, QDialog
)
from PySide6.QtCore import Signal

from config import MATRIX_COLORS
from utils.ssh_client import SSHClient
from utils.config_manager import SSHConfigManager
from utils.app_settings import AppSettings
from ui.ssh_browser import SSHBrowserDialog
from ui.widgets.styles import action_button_style, save_button_style

logger = logging.getLogger(__name__)


class SSHTab(QWidget):
    """SSH server configuration and connection tab."""

    message = Signal(str, str)  # message, type

    def __init__(self, config_manager: SSHConfigManager,
                 app_settings: AppSettings, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.app_settings = app_settings
        self._init_ui()
        self.load_saved_configs()

    def _init_ui(self):
        ssh_layout = QVBoxLayout()
        ssh_layout.setContentsMargins(10, 10, 10, 10)
        ssh_layout.setSpacing(10)

        # Saved configurations
        ssh_saved_group = QGroupBox(">> CONFIGURACIONES GUARDADAS")
        ssh_saved_layout = QHBoxLayout()
        ssh_saved_layout.setContentsMargins(10, 10, 10, 10)

        self.config_combo = QComboBox()
        self.config_combo.setPlaceholderText("Selecciona una configuracion guardada...")
        self.config_combo.currentTextChanged.connect(self._load_config)
        ssh_saved_layout.addWidget(QLabel("Configuracion:"))
        ssh_saved_layout.addWidget(self.config_combo)

        load_button = QPushButton("Cargar")
        load_button.clicked.connect(lambda: self._load_config(self.config_combo.currentText()))
        ssh_saved_layout.addWidget(load_button)

        save_button = QPushButton("Guardar")
        save_button.setStyleSheet(save_button_style())
        save_button.clicked.connect(self.save_current_config)
        ssh_saved_layout.addWidget(save_button)

        ssh_saved_group.setLayout(ssh_saved_layout)
        ssh_layout.addWidget(ssh_saved_group)

        # SSH Connection fields
        ssh_config_group = QGroupBox(">> CONEXION SSH")
        ssh_config_layout = QFormLayout()
        ssh_config_layout.setContentsMargins(10, 15, 10, 10)
        ssh_config_layout.setSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre para esta configuracion (ej: Servidor Casa)")
        ssh_config_layout.addRow("Nombre:", self.name_input)

        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("ejemplo: 192.168.1.100 o servidor.com")
        ssh_config_layout.addRow("Host:", self.host_input)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("22")
        self.port_input.setText("22")
        ssh_config_layout.addRow("Puerto:", self.port_input)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("usuario")
        ssh_config_layout.addRow("Usuario:", self.user_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("contrasena (opcional si usas clave)")
        self.password_input.setEchoMode(QLineEdit.Password)
        ssh_config_layout.addRow("Contrasena:", self.password_input)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("ruta a clave privada (opcional)")
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_input)
        key_button = QPushButton("Buscar...")
        key_button.clicked.connect(self._select_key)
        key_layout.addWidget(key_button)
        ssh_config_layout.addRow("Clave SSH:", key_layout)

        ssh_config_group.setLayout(ssh_config_layout)
        ssh_layout.addWidget(ssh_config_group)

        # Remote folder
        ssh_folder_group = QGroupBox(">> CARPETA REMOTA")
        ssh_folder_layout = QVBoxLayout()
        ssh_folder_layout.setContentsMargins(10, 10, 10, 10)
        ssh_folder_layout.setSpacing(8)

        folder_input_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("ejemplo: /home/usuario/Descargas")
        last_remote = self.app_settings.get_last_remote_folder()
        if last_remote:
            self.folder_input.setText(last_remote)
        self.folder_input.editingFinished.connect(self._save_folder)
        folder_input_layout.addWidget(self.folder_input)

        browse_button = QPushButton("Explorar...")
        browse_button.setStyleSheet(action_button_style('info'))
        browse_button.clicked.connect(self._browse_folder)
        folder_input_layout.addWidget(browse_button)

        ssh_folder_layout.addLayout(folder_input_layout)

        test_button = QPushButton("Probar Conexion")
        test_button.setStyleSheet(action_button_style('info'))
        test_button.clicked.connect(self.test_connection)
        ssh_folder_layout.addWidget(test_button)

        clear_button = QPushButton("Limpiar Campos")
        clear_button.setStyleSheet(action_button_style('warning'))
        clear_button.clicked.connect(self.clear_fields)
        ssh_folder_layout.addWidget(clear_button)

        ssh_folder_group.setLayout(ssh_folder_layout)
        ssh_layout.addWidget(ssh_folder_group)
        ssh_layout.addStretch()
        self.setLayout(ssh_layout)

    def load_saved_configs(self):
        configs = self.config_manager.load_configs()
        self.config_combo.clear()
        self.config_combo.addItem("-- Nueva configuracion --", None)
        for config in configs:
            name = config.get('name', 'Sin nombre')
            self.config_combo.addItem(name, config)

    def _load_config(self, text):
        if text == "-- Nueva configuracion --":
            return
        index = self.config_combo.currentIndex()
        if index > 0:
            configs = self.config_manager.load_configs()
            if index - 1 < len(configs):
                config = configs[index - 1]
                self.name_input.setText(config.get('name', ''))
                self.host_input.setText(config.get('host', ''))
                self.port_input.setText(str(config.get('port', 22)))
                self.user_input.setText(config.get('username', ''))
                self.password_input.setText(config.get('password', ''))
                self.key_input.setText(config.get('key_file', ''))
                self.folder_input.setText(config.get('remote_folder', ''))

    def save_current_config(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Introduce un nombre para la configuracion")
            return
        host = self.host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Error", "Introduce el host del servidor")
            return
        try:
            port = int(self.port_input.text().strip() or "22")
        except ValueError:
            QMessageBox.warning(self, "Error", "El puerto debe ser un numero")
            return
        username = self.user_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Introduce el usuario")
            return

        password = self.password_input.text()
        key_file = self.key_input.text().strip()
        remote_folder = self.folder_input.text().strip()

        success = self.config_manager.save_config(
            name=name, host=host, port=port, username=username,
            password=password, key_file=key_file,
            remote_folder=remote_folder, description=f"Servidor SSH: {host}"
        )

        if success:
            self.message.emit(f"Configuracion '{name}' guardada", "success")
            self.load_saved_configs()
            index = self.config_combo.findText(name)
            if index >= 0:
                self.config_combo.setCurrentIndex(index)
            QMessageBox.information(self, "Exito", f"Configuracion '{name}' guardada")
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar la configuracion")

    def clear_fields(self):
        self.name_input.clear()
        self.host_input.clear()
        self.port_input.setText("22")
        self.user_input.clear()
        self.password_input.clear()
        self.key_input.clear()
        self.folder_input.clear()
        self.message.emit("Campos SSH limpiados", "info")

    def test_connection(self):
        if not self.validate_inputs():
            return
        self.message.emit("Probando conexion SSH...", "info")
        try:
            ssh_client = SSHClient()
            host = self.host_input.text().strip()
            port = int(self.port_input.text().strip() or "22")
            username = self.user_input.text().strip()
            password = self.password_input.text().strip() or None
            key_file = self.key_input.text().strip() or None

            success, msg = ssh_client.connect(host, port, username, password, key_file)
            if success:
                test_ok, test_msg = ssh_client.test_connection()
                ssh_client.disconnect()
                if test_ok:
                    self.message.emit("Conexion SSH exitosa!", "success")
                    QMessageBox.information(self, "Conexion Exitosa", "Conexion SSH establecida.")
                else:
                    self.message.emit(f"Advertencia: {test_msg}", "warning")
            else:
                self.message.emit(f"Error de conexion: {msg}", "error")
                QMessageBox.warning(self, "Error de Conexion", msg)
        except ValueError:
            self.message.emit("El puerto debe ser un numero", "error")
        except Exception as e:
            logger.exception("SSH connection test failed")
            self.message.emit(f"Error: {str(e)}", "error")

    def validate_inputs(self) -> bool:
        if not self.host_input.text().strip():
            QMessageBox.warning(self, "Error", "Introduce el host del servidor SSH")
            return False
        if not self.user_input.text().strip():
            QMessageBox.warning(self, "Error", "Introduce el usuario SSH")
            return False
        try:
            port = self.port_input.text().strip()
            if port and not (1 <= int(port) <= 65535):
                QMessageBox.warning(self, "Error", "El puerto debe estar entre 1 y 65535")
                return False
        except ValueError:
            QMessageBox.warning(self, "Error", "El puerto debe ser un numero")
            return False
        return True

    def get_config_dict(self) -> dict:
        try:
            return {
                'host': self.host_input.text().strip(),
                'port': int(self.port_input.text().strip() or "22"),
                'username': self.user_input.text().strip(),
                'password': self.password_input.text().strip() or None,
                'key_file': self.key_input.text().strip() or None,
                'remote_folder': self.folder_input.text().strip()
            }
        except ValueError:
            return None

    def get_remote_folder(self) -> str:
        return self.folder_input.text().strip()

    def _select_key(self):
        key_file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Clave SSH",
            str(Path.home() / ".ssh"), "Claves SSH (*);;Todos (*)"
        )
        if key_file:
            self.key_input.setText(key_file)

    def _browse_folder(self):
        if not self.validate_inputs():
            QMessageBox.warning(self, "Error",
                "Completa la configuracion SSH (Host y Usuario) antes de explorar")
            return
        ssh_config = self.get_config_dict()
        if not ssh_config:
            QMessageBox.warning(self, "Error", "Error en configuracion SSH. Verifica el puerto.")
            return
        browser = SSHBrowserDialog(self, ssh_config)
        if browser.exec() == QDialog.Accepted:
            selected = browser.get_selected_path()
            if selected:
                self.folder_input.setText(selected)
                self.app_settings.set_last_remote_folder(selected)
                self.message.emit(f"Carpeta seleccionada: {selected}", "success")

    def _save_folder(self):
        folder = self.folder_input.text().strip()
        if folder:
            self.app_settings.set_last_remote_folder(folder)
```

**Step 2: Commit**

```bash
git add ui/widgets/ssh_tab.py
git commit -m "refactor: extract SSHTab widget from main_window"
```

---

### Task 6: Create progress_widget.py (Progress + Status + Log)

**Files:**
- Create: `ui/widgets/progress_widget.py`

**Step 1: Create progress widget**

Create `ui/widgets/progress_widget.py` extracting lines 650-674 from `main_window.py` plus log enhancements (timestamps, copy button):

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Widget for download progress, status display, and message log."""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QTextEdit, QGroupBox, QPushButton, QApplication
)
from PySide6.QtCore import Qt

from config import MATRIX_COLORS
from ui.widgets.styles import action_button_style


class ProgressWidget(QWidget):
    """Progress bar, status label, and enhanced message log."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - %v")
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel(">> SISTEMA LISTO")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            f"font-size: 12pt; font-weight: bold; color: {MATRIX_COLORS['accent']}; "
            f"padding: 8px; font-family: 'Consolas', monospace;"
        )
        layout.addWidget(self.status_label)

        # Log area
        log_group = QGroupBox(">> LOG")
        log_layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)

        # Log buttons
        log_buttons = QHBoxLayout()
        copy_button = QPushButton("Copiar Log")
        copy_button.setStyleSheet(action_button_style('info'))
        copy_button.clicked.connect(self._copy_log)
        log_buttons.addWidget(copy_button)

        clear_button = QPushButton("Limpiar Log")
        clear_button.setStyleSheet(action_button_style('error'))
        clear_button.clicked.connect(self.clear_log)
        log_buttons.addWidget(clear_button)
        log_buttons.addStretch()

        log_layout.addLayout(log_buttons)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        self.setLayout(layout)

    def update_progress(self, percent: int, message: str):
        self.progress_bar.setValue(percent)
        self.status_label.setText(f">> {message}")

    def set_status(self, text: str):
        self.status_label.setText(text)

    def add_message(self, message: str, message_type: str = "info"):
        colors = {
            "info": MATRIX_COLORS["info"],
            "success": MATRIX_COLORS["success"],
            "error": MATRIX_COLORS["error"],
            "warning": MATRIX_COLORS["warning"],
        }
        color = colors.get(message_type, MATRIX_COLORS["text"])
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(
            f'<span style="color: {MATRIX_COLORS["text_dim"]};">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">[{message_type.upper()}]</span> '
            f'<span style="color: {MATRIX_COLORS["text"]};">{message}</span>'
        )

    def clear_log(self):
        self.log_text.clear()

    def reset(self):
        self.progress_bar.setValue(0)
        self.status_label.setText(">> SISTEMA LISTO")

    def _copy_log(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.log_text.toPlainText())
        self.add_message("Log copiado al portapapeles", "info")
```

**Step 2: Commit**

```bash
git add ui/widgets/progress_widget.py
git commit -m "refactor: extract ProgressWidget with timestamps and copy button"
```

---

### Task 7: Add logging module

**Files:**
- Create: `utils/logger.py`

**Step 1: Create logging setup**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Application logging configuration."""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Configure application-wide logging with file rotation."""
    log_dir = Path.home() / ".youtube_downloader"
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "app.log"

    root_logger = logging.getLogger("media_downloader")
    root_logger.setLevel(logging.DEBUG)

    # File handler with rotation (5MB, 3 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_fmt)

    # Console handler (INFO+)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_fmt)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    return root_logger
```

**Step 2: Update main.py to initialize logging**

In `main.py`, add before `app = QApplication(...)`:

```python
from utils.logger import setup_logging
setup_logging()
```

**Step 3: Commit**

```bash
git add utils/logger.py main.py
git commit -m "feat: add formal logging with file rotation"
```

---

### Task 8: Fix SSH security issues

**Files:**
- Modify: `utils/ssh_client.py`
- Modify: `requirements.txt`

**Step 1: Update requirements.txt**

Add `keyring>=24.0.0` to requirements.txt.

**Step 2: Rewrite ssh_client.py with security fixes**

Key changes:
1. Replace `AutoAddPolicy()` with `WarningPolicy()` and fall back to known_hosts
2. Remove entire SCP/sshpass fallback (lines 229-284)
3. Replace bare `except:` with specific exceptions
4. Add `sftp.put()` callback for upload progress
5. Add proper logging

The `disconnect` method (line 102-110) changes from:
```python
try:
    ...
except:
    pass
```
To:
```python
try:
    if self.sftp:
        self.sftp.close()
    if self.client:
        self.client.close()
except (paramiko.SSHException, OSError) as e:
    logger.warning("Error closing SSH connection: %s", e)
finally:
    self.sftp = None
    self.client = None
```

The `upload_file` method removes the entire SCP fallback block (lines 229-284) and uses `sftp.put()` with a proper callback:
```python
self.sftp.put(local_path, remote_path, callback=progress_callback)
```

The `file_exists` and `get_file_size` bare excepts change to:
```python
except (IOError, OSError):
```

**Step 3: Fix bare excepts in ssh_browser.py**

Change `ssh_browser.py:291` and `ssh_browser.py:337` from `except:` to `except (IOError, OSError):` and `except Exception as e:` respectively.

**Step 4: Commit**

```bash
git add utils/ssh_client.py ui/ssh_browser.py requirements.txt
git commit -m "fix: security improvements - remove sshpass, fix bare excepts, add WarningPolicy"
```

---

### Task 9: Rewrite main_window.py using widgets

**Files:**
- Modify: `ui/main_window.py` (complete rewrite using new widgets)

**Step 1: Rewrite main_window.py**

Replace the entire 1430-line file with an orchestrator (~300 lines) that:
1. Imports and composes all widgets
2. Uses `QThread` instead of `threading.Thread`
3. Adds cancel button with `threading.Event`
4. Connects widget signals
5. Has keyboard shortcuts (Ctrl+D download, Esc cancel)
6. Shows version in title bar
7. Uses centralized styles

Key structure:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main application window - orchestrates widgets."""

import logging
import os
import tempfile
from pathlib import Path
from threading import Event, Thread

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont, QShortcut, QKeySequence

from config import (
    APP_NAME, APP_VERSION, MATRIX_COLORS,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_X, WINDOW_Y
)
from download.downloader import YouTubeDownloader
from download.progress_hook import DownloadProgressHook
from download.transcriber import AudioTranscriber
from utils.validators import InputValidator
from utils.ssh_client import SSHClient
from utils.config_manager import SSHConfigManager
from utils.app_settings import AppSettings
from ui.widgets.styles import app_stylesheet, download_button_style, cancel_button_style
from ui.widgets.source_widget import SourceWidget
from ui.widgets.options_widget import OptionsWidget
from ui.widgets.local_tab import LocalTab
from ui.widgets.ssh_tab import SSHTab
from ui.widgets.progress_widget import ProgressWidget

logger = logging.getLogger(__name__)
```

The class uses the widgets, adds cancel support via `self._cancel_event = Event()`, keyboard shortcuts via `QShortcut`, and the download logic is simplified (temp file detection uses yt-dlp info_dict).

**Step 2: Update ssh_browser.py to use centralized styles**

Replace the `apply_matrix_theme` method to use:
```python
from ui.widgets.styles import dialog_stylesheet
self.setStyleSheet(dialog_stylesheet())
```

**Step 3: Commit**

```bash
git add ui/main_window.py ui/ssh_browser.py
git commit -m "refactor: rewrite main_window using widget composition, add cancel & shortcuts"
```

---

### Task 10: Add temp file cleanup

**Files:**
- Modify: `ui/main_window.py`

**Step 1: Add cleanup on startup**

Add to `__init__` of `YouTubeDownloaderApp`:

```python
self._cleanup_temp_files()
```

Method:
```python
def _cleanup_temp_files(self):
    """Remove orphaned temp files from previous runs."""
    temp_dir = os.path.join(tempfile.gettempdir(), "youtube_download")
    if os.path.exists(temp_dir):
        try:
            for f in os.listdir(temp_dir):
                fp = os.path.join(temp_dir, f)
                if os.path.isfile(fp):
                    os.remove(fp)
            logger.info("Cleaned temp directory: %s", temp_dir)
        except OSError as e:
            logger.warning("Could not clean temp dir: %s", e)
```

**Step 2: Commit**

```bash
git add ui/main_window.py
git commit -m "feat: cleanup orphaned temp files on app startup"
```

---

### Task 11: Update main.py entry point

**Files:**
- Modify: `main.py`

**Step 1: Update main.py with logging and version in title**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main entry point for Media Downloader."""

import sys

from PySide6.QtWidgets import QApplication

from config import APP_NAME
from ui.main_window import YouTubeDownloaderApp
from utils.logger import setup_logging


def main():
    setup_logging()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(APP_NAME)

    window = YouTubeDownloaderApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
```

**Step 2: Commit**

```bash
git add main.py
git commit -m "feat: update entry point with logging initialization"
```

---

### Task 12: Replace bare excepts across all remaining files

**Files:**
- Modify: `download/downloader.py`
- Modify: `download/transcriber.py`
- Modify: `utils/config_manager.py`
- Modify: `utils/app_settings.py`
- Modify: `utils/ssh_diagnostics.py`

**Step 1: Fix all bare excepts**

- `downloader.py:161`: Keep `except Exception` but add logging
- `transcriber.py:88,161`: Keep `except Exception` but add logging
- `config_manager.py:46,95,119`: Change to `except (json.JSONDecodeError, OSError)`
- `app_settings.py:44,62`: Change to `except (json.JSONDecodeError, OSError)`
- `ssh_diagnostics.py:89`: Change `except:` to `except (IOError, OSError)`

Add `import logging` and `logger = logging.getLogger(__name__)` to each file, replace `print()` in `ssh_diagnostics.py` with `logger.info/warning`.

**Step 2: Commit**

```bash
git add download/downloader.py download/transcriber.py utils/config_manager.py utils/app_settings.py utils/ssh_diagnostics.py
git commit -m "fix: replace bare excepts with specific exceptions and add logging"
```

---

### Task 13: Final integration test and polish

**Files:**
- Modify: `ui/widgets/__init__.py` (add convenience imports)

**Step 1: Update widgets __init__.py**

```python
from ui.widgets.source_widget import SourceWidget
from ui.widgets.options_widget import OptionsWidget
from ui.widgets.local_tab import LocalTab
from ui.widgets.ssh_tab import SSHTab
from ui.widgets.progress_widget import ProgressWidget
```

**Step 2: Manual verification**

Run: `cd /home/drago/Escritorio/PROYECTS/SCRIPTS/MEDIA_DOWNLOADER && python main.py`

Verify:
- App launches without errors
- Matrix theme applied correctly
- URL auto-detection works
- Platform dropdown changes format options
- Local folder picker works
- SSH tab loads saved configs
- Cancel button appears during download
- Ctrl+D starts download
- Esc cancels download
- Log shows timestamps
- Copy log works
- Whisper model selector appears when transcription is checked
- Version shows in title bar

**Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete Media Downloader v2.1.0 audit improvements

- Refactored main_window.py into 6 focused widgets
- Centralized QSS styles eliminating duplication
- Added formal logging with file rotation
- Fixed security: removed sshpass, replaced bare excepts
- Added cancel download button with keyboard shortcuts
- Added Whisper model selector dropdown
- Enhanced log with timestamps and copy button
- Temp file cleanup on startup
- SSH upload progress via paramiko callback"
```

---

## Summary of all tasks

| # | Task | Files | Estimate |
|---|------|-------|----------|
| 1 | Centralized styles | `ui/widgets/styles.py` | Foundation |
| 2 | Source widget | `ui/widgets/source_widget.py` | Widget |
| 3 | Options widget | `ui/widgets/options_widget.py` | Widget |
| 4 | Local tab | `ui/widgets/local_tab.py` | Widget |
| 5 | SSH tab | `ui/widgets/ssh_tab.py` | Widget |
| 6 | Progress widget | `ui/widgets/progress_widget.py` | Widget |
| 7 | Logging module | `utils/logger.py` | Backend |
| 8 | SSH security fixes | `utils/ssh_client.py` | Security |
| 9 | Rewrite main_window | `ui/main_window.py` | Core |
| 10 | Temp cleanup | `ui/main_window.py` | Backend |
| 11 | Update main.py | `main.py` | Entry |
| 12 | Fix bare excepts | Multiple utils/download | Quality |
| 13 | Integration test | Verification | Polish |
