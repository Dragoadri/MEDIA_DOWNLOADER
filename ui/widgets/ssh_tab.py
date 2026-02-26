#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget de pestana para configuracion SSH: servidores guardados,
credenciales, carpeta remota, prueba de conexion y explorador SSH.
"""

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
    """Pestana para configurar la conexion SSH y carpeta remota"""

    message = Signal(str, str)  # mensaje, tipo

    def __init__(self, config_manager: SSHConfigManager,
                 app_settings: AppSettings, parent=None):
        """
        Inicializa la pestana SSH.

        Args:
            config_manager: Gestor de configuraciones SSH
            app_settings: Gestor de configuraciones de la aplicacion
            parent: Widget padre
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.app_settings = app_settings
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget"""
        ssh_layout = QVBoxLayout()
        ssh_layout.setContentsMargins(10, 10, 10, 10)
        ssh_layout.setSpacing(10)

        # ── Configuraciones guardadas ──
        ssh_saved_group = QGroupBox(">> CONFIGURACIONES GUARDADAS")
        ssh_saved_layout = QHBoxLayout()
        ssh_saved_layout.setContentsMargins(10, 10, 10, 10)

        self.ssh_config_combo = QComboBox()
        self.ssh_config_combo.setPlaceholderText(
            "Selecciona una configuracion guardada..."
        )
        self.ssh_config_combo.currentTextChanged.connect(self._on_config_selected)
        ssh_saved_layout.addWidget(QLabel("Configuracion:"))
        ssh_saved_layout.addWidget(self.ssh_config_combo)

        ssh_load_button = QPushButton("Cargar")
        ssh_load_button.clicked.connect(self._load_selected_config)
        ssh_saved_layout.addWidget(ssh_load_button)

        ssh_save_button = QPushButton("Guardar")
        ssh_save_button.setStyleSheet(save_button_style())
        ssh_save_button.clicked.connect(self.save_current_config)
        ssh_saved_layout.addWidget(ssh_save_button)

        ssh_saved_group.setLayout(ssh_saved_layout)
        ssh_layout.addWidget(ssh_saved_group)

        # ── Configuracion SSH ──
        ssh_config_group = QGroupBox(">> CONEXION SSH")
        ssh_config_layout = QFormLayout()
        ssh_config_layout.setContentsMargins(10, 15, 10, 10)
        ssh_config_layout.setSpacing(8)

        self.ssh_name_input = QLineEdit()
        self.ssh_name_input.setPlaceholderText(
            "Nombre para esta configuracion (ej: Servidor Casa)"
        )
        ssh_config_layout.addRow("Nombre:", self.ssh_name_input)

        self.ssh_host_input = QLineEdit()
        self.ssh_host_input.setPlaceholderText(
            "ejemplo: 192.168.1.100 o servidor.com"
        )
        ssh_config_layout.addRow("Host:", self.ssh_host_input)

        self.ssh_port_input = QLineEdit()
        self.ssh_port_input.setPlaceholderText("22")
        self.ssh_port_input.setText("22")
        ssh_config_layout.addRow("Puerto:", self.ssh_port_input)

        self.ssh_user_input = QLineEdit()
        self.ssh_user_input.setPlaceholderText("usuario")
        ssh_config_layout.addRow("Usuario:", self.ssh_user_input)

        self.ssh_password_input = QLineEdit()
        self.ssh_password_input.setPlaceholderText(
            "contrasena (opcional si usas clave)"
        )
        self.ssh_password_input.setEchoMode(QLineEdit.Password)
        ssh_config_layout.addRow("Contrasena:", self.ssh_password_input)

        self.ssh_key_input = QLineEdit()
        self.ssh_key_input.setPlaceholderText("ruta a clave privada (opcional)")
        ssh_key_layout = QHBoxLayout()
        ssh_key_layout.addWidget(self.ssh_key_input)
        ssh_key_button = QPushButton("Buscar...")
        ssh_key_button.clicked.connect(self._select_ssh_key)
        ssh_key_layout.addWidget(ssh_key_button)
        ssh_config_layout.addRow("Clave SSH:", ssh_key_layout)

        ssh_config_group.setLayout(ssh_config_layout)
        ssh_layout.addWidget(ssh_config_group)

        # ── Carpeta remota ──
        ssh_folder_group = QGroupBox(">> CARPETA REMOTA")
        ssh_folder_layout = QVBoxLayout()
        ssh_folder_layout.setContentsMargins(10, 10, 10, 10)
        ssh_folder_layout.setSpacing(8)

        # Campo y boton explorar
        folder_input_layout = QHBoxLayout()
        self.ssh_folder_input = QLineEdit()
        self.ssh_folder_input.setPlaceholderText(
            "ejemplo: /home/usuario/Descargas"
        )

        # Cargar ultima carpeta remota usada
        last_remote_folder = self.app_settings.get_last_remote_folder()
        if last_remote_folder:
            self.ssh_folder_input.setText(last_remote_folder)

        # Guardar automaticamente cuando el usuario termine de editar
        self.ssh_folder_input.editingFinished.connect(self._save_ssh_folder)
        folder_input_layout.addWidget(self.ssh_folder_input)

        ssh_browse_button = QPushButton("Explorar...")
        ssh_browse_button.setStyleSheet(action_button_style('info'))
        ssh_browse_button.clicked.connect(self._browse_ssh_folder)
        folder_input_layout.addWidget(ssh_browse_button)

        ssh_folder_layout.addLayout(folder_input_layout)

        # Boton probar conexion
        ssh_test_button = QPushButton("Probar Conexion")
        ssh_test_button.setStyleSheet(action_button_style('info'))
        ssh_test_button.clicked.connect(self.test_connection)
        ssh_folder_layout.addWidget(ssh_test_button)

        # Boton limpiar campos
        ssh_clear_button = QPushButton("Limpiar Campos")
        ssh_clear_button.setStyleSheet(action_button_style('warning'))
        ssh_clear_button.clicked.connect(self.clear_fields)
        ssh_folder_layout.addWidget(ssh_clear_button)

        ssh_folder_group.setLayout(ssh_folder_layout)
        ssh_layout.addWidget(ssh_folder_group)
        ssh_layout.addStretch()
        self.setLayout(ssh_layout)

    # ── Carga y guardado de configuraciones ──

    def load_saved_configs(self):
        """Carga las configuraciones SSH guardadas en el ComboBox"""
        configs = self.config_manager.load_configs()
        self.ssh_config_combo.clear()
        self.ssh_config_combo.addItem("-- Nueva configuracion --", None)
        for config in configs:
            name = config.get('name', 'Sin nombre')
            self.ssh_config_combo.addItem(name, config)

        # Si hay configuraciones, seleccionar "Servidor Casa" si existe
        for i in range(self.ssh_config_combo.count()):
            if self.ssh_config_combo.itemText(i) == "Servidor Casa":
                self.ssh_config_combo.setCurrentIndex(i)
                break

    def _on_config_selected(self, text):
        """Carga una configuracion SSH cuando se selecciona del ComboBox"""
        if text == "-- Nueva configuracion --":
            return

        index = self.ssh_config_combo.currentIndex()
        if index > 0:
            configs = self.config_manager.load_configs()
            if index - 1 < len(configs):
                config = configs[index - 1]
                self.ssh_name_input.setText(config.get('name', ''))
                self.ssh_host_input.setText(config.get('host', ''))
                self.ssh_port_input.setText(str(config.get('port', 22)))
                self.ssh_user_input.setText(config.get('username', ''))
                self.ssh_password_input.setText(config.get('password', ''))
                self.ssh_key_input.setText(config.get('key_file', ''))
                self.ssh_folder_input.setText(config.get('remote_folder', ''))

    def _load_selected_config(self):
        """Carga la configuracion SSH seleccionada"""
        self._on_config_selected(self.ssh_config_combo.currentText())

    def save_current_config(self):
        """Guarda la configuracion SSH actual"""
        name = self.ssh_name_input.text().strip()
        if not name:
            QMessageBox.warning(
                self, "Error",
                "Por favor, introduce un nombre para la configuracion"
            )
            return

        host = self.ssh_host_input.text().strip()
        if not host:
            QMessageBox.warning(
                self, "Error",
                "Por favor, introduce el host del servidor"
            )
            return

        try:
            port = int(self.ssh_port_input.text().strip() or "22")
        except ValueError:
            QMessageBox.warning(self, "Error", "El puerto debe ser un numero")
            return

        username = self.ssh_user_input.text().strip()
        if not username:
            QMessageBox.warning(
                self, "Error",
                "Por favor, introduce el usuario"
            )
            return

        password = self.ssh_password_input.text()
        key_file = self.ssh_key_input.text().strip()
        remote_folder = self.ssh_folder_input.text().strip()

        success = self.config_manager.save_config(
            name=name,
            host=host,
            port=port,
            username=username,
            password=password,
            key_file=key_file,
            remote_folder=remote_folder,
            description=f"Servidor SSH: {host}"
        )

        if success:
            logger.info("Configuracion SSH '%s' guardada correctamente", name)
            self.message.emit(
                f"Configuracion '{name}' guardada correctamente", "success"
            )
            self.load_saved_configs()
            # Seleccionar la configuracion guardada
            index = self.ssh_config_combo.findText(name)
            if index >= 0:
                self.ssh_config_combo.setCurrentIndex(index)
            QMessageBox.information(
                self, "Exito",
                f"Configuracion '{name}' guardada correctamente"
            )
        else:
            logger.error("No se pudo guardar la configuracion SSH '%s'", name)
            QMessageBox.warning(
                self, "Error",
                "No se pudo guardar la configuracion"
            )

    def clear_fields(self):
        """Limpia todos los campos SSH"""
        self.ssh_name_input.setText("")
        self.ssh_host_input.setText("")
        self.ssh_port_input.setText("22")
        self.ssh_user_input.setText("")
        self.ssh_password_input.setText("")
        self.ssh_key_input.setText("")
        self.ssh_folder_input.setText("")
        self.message.emit("Campos SSH limpiados", "info")

    # ── Conexion y exploracion ──

    def test_connection(self):
        """Prueba la conexion SSH"""
        if not self.validate_inputs():
            return

        self.message.emit("Probando conexion SSH...", "info")

        try:
            ssh_client = SSHClient()
            host = self.ssh_host_input.text().strip()
            port = int(self.ssh_port_input.text().strip() or "22")
            username = self.ssh_user_input.text().strip()
            password = self.ssh_password_input.text().strip() or None
            key_file = self.ssh_key_input.text().strip() or None

            success, msg = ssh_client.connect(host, port, username, password, key_file)

            if success:
                test_success, test_msg = ssh_client.test_connection()
                ssh_client.disconnect()

                if test_success:
                    logger.info("Conexion SSH exitosa a %s@%s:%d", username, host, port)
                    self.message.emit("Conexion SSH exitosa!", "success")
                    QMessageBox.information(
                        self, "Conexion Exitosa",
                        "La conexion SSH se establecio correctamente."
                    )
                else:
                    logger.warning("Prueba de conexion SSH fallida: %s", test_msg)
                    self.message.emit(f"Advertencia: {test_msg}", "warning")
            else:
                logger.error("Error de conexion SSH a %s:%d: %s", host, port, msg)
                self.message.emit(f"Error de conexion: {msg}", "error")
                QMessageBox.warning(self, "Error de Conexion", msg)

        except ValueError:
            self.message.emit("El puerto debe ser un numero", "error")
        except Exception as e:
            logger.exception("Error inesperado al probar conexion SSH")
            self.message.emit(f"Error: {str(e)}", "error")

    def validate_inputs(self) -> bool:
        """
        Valida los campos de entrada SSH.

        Returns:
            True si los campos son validos
        """
        if not self.ssh_host_input.text().strip():
            QMessageBox.warning(
                self, "Error",
                "Por favor, introduce el host del servidor SSH"
            )
            return False

        if not self.ssh_user_input.text().strip():
            QMessageBox.warning(
                self, "Error",
                "Por favor, introduce el usuario SSH"
            )
            return False

        try:
            port = self.ssh_port_input.text().strip()
            if port and (int(port) < 1 or int(port) > 65535):
                QMessageBox.warning(
                    self, "Error",
                    "El puerto debe estar entre 1 y 65535"
                )
                return False
        except ValueError:
            QMessageBox.warning(self, "Error", "El puerto debe ser un numero")
            return False

        return True

    def get_config_dict(self) -> dict:
        """
        Obtiene la configuracion SSH actual como diccionario.

        Returns:
            Diccionario con la configuracion SSH, o None si hay error
        """
        try:
            return {
                'host': self.ssh_host_input.text().strip(),
                'port': int(self.ssh_port_input.text().strip() or "22"),
                'username': self.ssh_user_input.text().strip(),
                'password': self.ssh_password_input.text().strip() or None,
                'key_file': self.ssh_key_input.text().strip() or None
            }
        except ValueError:
            logger.error("Puerto SSH invalido: %s", self.ssh_port_input.text())
            return None

    def get_remote_folder(self) -> str:
        """Retorna la carpeta remota configurada"""
        return self.ssh_folder_input.text().strip()

    # ── Metodos privados ──

    def _select_ssh_key(self):
        """Abre un dialogo para seleccionar el archivo de clave SSH"""
        key_file, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Clave SSH",
            str(Path.home() / ".ssh"),
            "Claves SSH (*);;Todos los archivos (*)"
        )
        if key_file:
            self.ssh_key_input.setText(key_file)

    def _browse_ssh_folder(self):
        """Abre el explorador de carpetas SSH"""
        if not self.validate_inputs():
            QMessageBox.warning(
                self, "Error",
                "Por favor, completa la configuracion SSH (Host y Usuario) antes de explorar"
            )
            return

        ssh_config = self.get_config_dict()
        if not ssh_config:
            QMessageBox.warning(
                self, "Error",
                "Error en la configuracion SSH. Verifica el puerto."
            )
            return

        browser = SSHBrowserDialog(self, ssh_config)

        if browser.exec() == QDialog.Accepted:
            selected_path = browser.get_selected_path()
            if selected_path:
                self.ssh_folder_input.setText(selected_path)
                self.app_settings.set_last_remote_folder(selected_path)
                self.message.emit(
                    f"Carpeta seleccionada: {selected_path}", "success"
                )

    def _save_ssh_folder(self):
        """Guarda la carpeta SSH actual como predeterminada"""
        folder = self.ssh_folder_input.text().strip()
        if folder:
            self.app_settings.set_last_remote_folder(folder)
