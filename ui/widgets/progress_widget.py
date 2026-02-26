#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget de progreso con barra, estado y log mejorado.
Incluye timestamps, boton de copiar y boton de limpiar.
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QTextEdit, QPushButton, QGroupBox, QApplication
)
from PySide6.QtCore import Qt

from config import MATRIX_COLORS
from ui.widgets.styles import cancel_button_style, action_button_style


class ProgressWidget(QWidget):
    """Widget de progreso con barra, estado y log con timestamps"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - %v")
        layout.addWidget(self.progress_bar)

        # Mensaje de estado
        self.status_label = QLabel(">> SISTEMA LISTO")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            f"font-size: 12pt; font-weight: bold; color: {MATRIX_COLORS['accent']}; "
            f"padding: 8px; font-family: 'Consolas', monospace;"
        )
        layout.addWidget(self.status_label)

        # Area de mensajes (log)
        messages_group = QGroupBox(">> LOG")
        messages_layout = QVBoxLayout()

        self.messages_text = QTextEdit()
        self.messages_text.setReadOnly(True)
        self.messages_text.setMaximumHeight(120)
        messages_layout.addWidget(self.messages_text)

        # Botones de log
        log_buttons_layout = QHBoxLayout()

        copy_button = QPushButton("Copiar Log")
        copy_button.setStyleSheet(action_button_style('info'))
        copy_button.setToolTip("Copia el contenido del log al portapapeles")
        copy_button.clicked.connect(self._copy_log)
        log_buttons_layout.addWidget(copy_button)

        clear_button = QPushButton("Limpiar Log")
        clear_button.setStyleSheet(cancel_button_style())
        clear_button.clicked.connect(self.clear_log)
        log_buttons_layout.addWidget(clear_button)

        log_buttons_layout.addStretch()
        messages_layout.addLayout(log_buttons_layout)

        messages_group.setLayout(messages_layout)
        layout.addWidget(messages_group)

        self.setLayout(layout)

    def update_progress(self, percent: int, message: str):
        """
        Actualiza la barra de progreso y el mensaje de estado.

        Args:
            percent: Porcentaje de progreso (0-100)
            message: Mensaje de estado
        """
        self.progress_bar.setValue(percent)
        self.status_label.setText(f">> {message}")

    def set_status(self, text: str):
        """
        Establece el texto de estado.

        Args:
            text: Texto a mostrar en la etiqueta de estado
        """
        self.status_label.setText(text)

    def add_message(self, message: str, message_type: str = "info"):
        """
        Anade un mensaje al log con timestamp.

        Args:
            message: Mensaje a mostrar
            message_type: Tipo de mensaje (info, success, error, warning)
        """
        colors = {
            "info": MATRIX_COLORS["info"],
            "success": MATRIX_COLORS["success"],
            "error": MATRIX_COLORS["error"],
            "warning": MATRIX_COLORS["warning"]
        }
        color = colors.get(message_type, MATRIX_COLORS["text"])
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.messages_text.append(
            f'<span style="color: {MATRIX_COLORS["text_dim"]};">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">[{message_type.upper()}]</span> '
            f'<span style="color: {MATRIX_COLORS["text"]};">{message}</span>'
        )

    def clear_log(self):
        """Limpia el area de mensajes"""
        self.messages_text.clear()

    def reset(self):
        """Reinicia el widget a su estado inicial"""
        self.progress_bar.setValue(0)
        self.status_label.setText(">> SISTEMA LISTO")
        self.messages_text.clear()

    def _copy_log(self):
        """Copia el contenido del log como texto plano al portapapeles"""
        plain_text = self.messages_text.toPlainText()
        if plain_text:
            clipboard = QApplication.clipboard()
            clipboard.setText(plain_text)
