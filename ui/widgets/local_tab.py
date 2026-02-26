#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget de pestana para configurar la carpeta de descarga local.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QFileDialog
)
from PySide6.QtCore import Signal

from config import DEFAULT_DOWNLOAD_FOLDER
from utils.app_settings import AppSettings


class LocalTab(QWidget):
    """Pestana para seleccionar la carpeta de descarga local"""

    folder_changed = Signal(str)

    def __init__(self, app_settings: AppSettings, parent=None):
        """
        Inicializa la pestana local.

        Args:
            app_settings: Gestor de configuraciones de la aplicacion
            parent: Widget padre
        """
        super().__init__(parent)
        self.app_settings = app_settings
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        local_folder_group = QGroupBox(">> CARPETA LOCAL")
        local_folder_layout = QHBoxLayout()
        local_folder_layout.setContentsMargins(10, 10, 10, 10)

        self.local_folder_input = QLineEdit()
        self.local_folder_input.setPlaceholderText(
            "Selecciona la carpeta donde guardar el archivo..."
        )

        # Cargar ultima carpeta usada o usar la predeterminada
        last_local_folder = self.app_settings.get_last_local_folder()
        self.local_folder_input.setText(last_local_folder or DEFAULT_DOWNLOAD_FOLDER)

        # Guardar automaticamente cuando el usuario termine de editar
        self.local_folder_input.editingFinished.connect(self._save_local_folder)

        local_folder_button = QPushButton("Buscar...")
        local_folder_button.clicked.connect(self._select_local_folder)

        local_folder_layout.addWidget(self.local_folder_input)
        local_folder_layout.addWidget(local_folder_button)

        local_folder_group.setLayout(local_folder_layout)
        layout.addWidget(local_folder_group)
        layout.addStretch()
        self.setLayout(layout)

    def _save_local_folder(self):
        """Guarda la carpeta local actual como predeterminada"""
        folder = self.local_folder_input.text().strip()
        if folder:
            self.app_settings.set_last_local_folder(folder)
            self.folder_changed.emit(folder)

    def _select_local_folder(self):
        """Abre un dialogo para seleccionar la carpeta de destino local"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta de Destino",
            self.local_folder_input.text()
        )
        if folder:
            self.local_folder_input.setText(folder)
            self.app_settings.set_last_local_folder(folder)
            self.folder_changed.emit(folder)

    def get_folder(self) -> str:
        """Retorna la carpeta local seleccionada"""
        return self.local_folder_input.text().strip()
