#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget de seleccion de plataforma y entrada de URL.
Detecta automaticamente la plataforma a partir de la URL.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QGroupBox
)
from PySide6.QtCore import Signal

from config import SUPPORTED_PLATFORMS, MATRIX_COLORS
from utils.validators import InputValidator
from ui.widgets.styles import valid_field_style, invalid_field_style, neutral_field_style


class SourceWidget(QWidget):
    """Widget para seleccionar plataforma e introducir URL"""

    url_changed = Signal(str)
    platform_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget"""
        group = QGroupBox(">> FUENTE")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(12)

        # Selector de plataforma
        platform_layout = QHBoxLayout()
        platform_label = QLabel("Plataforma:")
        platform_label.setMinimumWidth(90)
        self.platform_combo = QComboBox()

        # Anadir plataformas con iconos
        for platform_name, platform_info in SUPPORTED_PLATFORMS.items():
            icon = platform_info.get("icon", "")
            self.platform_combo.addItem(f"{icon} {platform_name}", platform_name)

        self.platform_combo.currentIndexChanged.connect(self._on_platform_changed)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_combo, 1)
        group_layout.addLayout(platform_layout)

        # Campo URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        url_label.setMinimumWidth(90)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pega aquí la URL del contenido...")
        self.url_input.textChanged.connect(self._on_url_changed)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        group_layout.addLayout(url_layout)

        # Indicador de plataforma detectada
        self.detected_platform_label = QLabel("")
        self.detected_platform_label.setStyleSheet(
            f"color: {MATRIX_COLORS['text_dim']}; font-size: 9pt; padding-left: 95px;"
        )
        group_layout.addWidget(self.detected_platform_label)

        group.setLayout(group_layout)

        # Layout principal del widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(group)
        self.setLayout(layout)

    def _on_platform_changed(self, index):
        """Se ejecuta cuando se cambia la plataforma seleccionada"""
        platform = self.platform_combo.currentData()
        if platform:
            self.platform_changed.emit(platform)

    def _on_url_changed(self, text):
        """Se ejecuta cuando cambia la URL para detectar plataforma automaticamente"""
        if text.strip():
            detected = InputValidator.detect_platform(text)
            if detected:
                self.detected_platform_label.setText(f"Detectado: {detected}")
                # Auto-seleccionar la plataforma detectada
                for i in range(self.platform_combo.count()):
                    if self.platform_combo.itemData(i) == detected:
                        self.platform_combo.setCurrentIndex(i)
                        break
        else:
            self.detected_platform_label.setText("")

        self.url_changed.emit(text)

    def get_url(self) -> str:
        """Retorna la URL actual"""
        return self.url_input.text().strip()

    def get_platform(self) -> str:
        """Retorna la plataforma seleccionada"""
        return self.platform_combo.currentData()

    def set_url_valid(self, valid: bool):
        """
        Aplica estilo visual al campo URL segun validez.

        Args:
            valid: True para borde verde, False para borde rojo, None para neutro
        """
        if valid is None:
            self.url_input.setStyleSheet(neutral_field_style())
        elif valid:
            self.url_input.setStyleSheet(valid_field_style())
        else:
            self.url_input.setStyleSheet(invalid_field_style())
