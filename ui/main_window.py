#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal de la aplicación
"""

import sys
import os
import tempfile
from pathlib import Path
from threading import Thread
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar, QComboBox,
    QFileDialog, QMessageBox, QTextEdit, QGroupBox, QRadioButton,
    QTabWidget, QFormLayout, QCheckBox, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont, QIcon

from config import (
    APP_NAME, DEFAULT_DOWNLOAD_FOLDER, VIDEO_QUALITIES,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_X, WINDOW_Y,
    SUPPORTED_PLATFORMS, MATRIX_COLORS
)
from download.progress_hook import DownloadProgressHook
from download.downloader import YouTubeDownloader
from download.transcriber import AudioTranscriber
from utils.validators import InputValidator
from utils.ssh_client import SSHClient
from utils.config_manager import SSHConfigManager
from utils.app_settings import AppSettings
from ui.ssh_browser import SSHBrowserDialog


class DownloadSignals(QObject):
    """Señales para comunicación entre hilos"""
    message = Signal(str, str)  # mensaje, tipo
    progress_update = Signal(int, str)  # porcentaje, mensaje
    show_dialog = Signal(str, str, str)  # título, mensaje, tipo (info/error/warning)
    download_finished = Signal(bool, str, str)  # éxito, mensaje, título


class YouTubeDownloaderApp(QMainWindow):
    """Aplicación principal para descargar contenido de YouTube"""
    
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.progress_hook = None
        self.ssh_client = None
        self.config_manager = SSHConfigManager()
        self.app_settings = AppSettings()
        self.download_signals = DownloadSignals()
        self.download_signals.message.connect(self.add_message)
        self.download_signals.progress_update.connect(self.update_progress)
        self.download_signals.show_dialog.connect(self.show_dialog_safe)
        self.download_signals.download_finished.connect(self.on_download_finished)
        self.init_ui()
        self.apply_styles()
        self.load_saved_ssh_configs()
        self.initialize_default_ssh_config()
    
    def show_dialog_safe(self, title, message, dialog_type):
        """Muestra un diálogo de forma segura desde cualquier hilo"""
        if dialog_type == "info":
            QMessageBox.information(self, title, message)
        elif dialog_type == "error":
            QMessageBox.critical(self, title, message)
        elif dialog_type == "warning":
            QMessageBox.warning(self, title, message)
    
    def on_download_finished(self, success, message, title):
        """Maneja la finalización de la descarga"""
        self.download_button.setEnabled(True)
        self.status_label.setText(">> SISTEMA LISTO")
        
        if success:
            self.download_signals.show_dialog.emit("Éxito", message, "info")
        else:
            self.download_signals.show_dialog.emit("Error", message, "error")
    
    def apply_styles(self):
        """Aplica estilos Matrix en modo oscuro a la aplicación"""
        mc = MATRIX_COLORS
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {mc['background']};
                color: {mc['text']};
            }}
            QWidget {{
                background-color: {mc['background']};
                color: {mc['text']};
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {mc['border_dim']};
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 15px;
                background-color: {mc['background_secondary']};
                color: {mc['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
                color: {mc['accent']};
                font-weight: bold;
            }}
            QLineEdit {{
                padding: 10px;
                border: 1px solid {mc['border_dim']};
                border-radius: 4px;
                font-size: 11pt;
                background-color: {mc['background_secondary']};
                color: {mc['text']};
                selection-background-color: {mc['accent_dark']};
                selection-color: {mc['text_bright']};
            }}
            QLineEdit:focus {{
                border: 1px solid {mc['accent']};
                background-color: {mc['background_tertiary']};
            }}
            QLineEdit::placeholder {{
                color: {mc['text_dim']};
            }}
            QPushButton {{
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11pt;
                background-color: {mc['background_tertiary']};
                color: {mc['text']};
                border: 1px solid {mc['border_dim']};
            }}
            QPushButton:hover {{
                background-color: {mc['accent_dark']};
                border: 1px solid {mc['accent']};
                color: {mc['text_bright']};
            }}
            QPushButton:pressed {{
                background-color: {mc['background_secondary']};
            }}
            QPushButton:disabled {{
                background-color: {mc['background']};
                color: {mc['border_dim']};
                border: 1px solid {mc['background_tertiary']};
            }}
            QComboBox {{
                padding: 10px;
                border: 1px solid {mc['border_dim']};
                border-radius: 4px;
                font-size: 11pt;
                background-color: {mc['background_secondary']};
                color: {mc['text']};
            }}
            QComboBox:hover {{
                border: 1px solid {mc['accent']};
            }}
            QComboBox:focus {{
                border: 1px solid {mc['accent']};
            }}
            QComboBox::drop-down {{
                border: none;
                background-color: {mc['background_tertiary']};
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {mc['text']};
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {mc['background_secondary']};
                color: {mc['text']};
                selection-background-color: {mc['accent_dark']};
                selection-color: {mc['text_bright']};
                border: 1px solid {mc['border_dim']};
                outline: none;
            }}
            QProgressBar {{
                border: 1px solid {mc['border_dim']};
                border-radius: 4px;
                text-align: center;
                height: 28px;
                font-weight: bold;
                background-color: {mc['background_secondary']};
                color: {mc['text']};
            }}
            QProgressBar::chunk {{
                background-color: {mc['accent']};
                border-radius: 3px;
            }}
            QTextEdit {{
                border: 1px solid {mc['border_dim']};
                border-radius: 4px;
                background-color: {mc['background']};
                color: {mc['text']};
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 10pt;
                selection-background-color: {mc['accent_dark']};
                selection-color: {mc['text_bright']};
                padding: 8px;
            }}
            QRadioButton {{
                font-size: 11pt;
                padding: 5px;
                color: {mc['text']};
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {mc['border_dim']};
                background-color: {mc['background_secondary']};
            }}
            QRadioButton::indicator:checked {{
                background-color: {mc['accent']};
                border: 2px solid {mc['accent']};
            }}
            QRadioButton::indicator:hover {{
                border: 2px solid {mc['accent']};
            }}
            QLabel {{
                font-size: 11pt;
                color: {mc['text']};
            }}
            QTabWidget::pane {{
                border: 1px solid {mc['border_dim']};
                border-radius: 4px;
                background-color: {mc['background_secondary']};
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: {mc['background_tertiary']};
                color: {mc['text_dim']};
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid {mc['border_dim']};
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background-color: {mc['background_secondary']};
                border-bottom: 2px solid {mc['accent']};
                color: {mc['accent']};
            }}
            QTabBar::tab:hover {{
                background-color: {mc['accent_dark']};
                color: {mc['text_bright']};
            }}
            QScrollArea {{
                border: none;
                background-color: {mc['background']};
            }}
            QScrollBar:vertical {{
                border: none;
                background-color: {mc['background_secondary']};
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {mc['accent_dark']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {mc['accent']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background-color: {mc['background_secondary']};
                height: 10px;
                margin: 0;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {mc['accent_dark']};
                border-radius: 5px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {mc['accent']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QCheckBox {{
                font-size: 11pt;
                color: {mc['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {mc['border_dim']};
                background-color: {mc['background_secondary']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {mc['accent']};
                border: 2px solid {mc['accent']};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid {mc['accent']};
            }}
        """)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH + 100, WINDOW_HEIGHT + 100)
        
        # Widget central con scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget contenedor
        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)
        
        # Título mejorado estilo Matrix
        title = QLabel(">> " + APP_NAME + " <<")
        title_font = QFont("Consolas", 24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {MATRIX_COLORS['accent']}; margin-bottom: 5px; font-weight: bold;")
        main_layout.addWidget(title)

        # Subtítulo con versión
        subtitle = QLabel("[ Multi-Platform Media Downloader v2.0 ]")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {MATRIX_COLORS['text_dim']}; font-size: 10pt; margin-bottom: 10px;")
        main_layout.addWidget(subtitle)

        # Grupo: Selección de Plataforma y URL
        source_group = QGroupBox(">> FUENTE")
        source_layout = QVBoxLayout()
        source_layout.setSpacing(12)

        # Selector de plataforma
        platform_layout = QHBoxLayout()
        platform_label = QLabel("Plataforma:")
        platform_label.setMinimumWidth(90)
        self.platform_combo = QComboBox()

        # Añadir plataformas con iconos
        for platform_name, platform_info in SUPPORTED_PLATFORMS.items():
            icon = platform_info.get("icon", "")
            self.platform_combo.addItem(f"{icon} {platform_name}", platform_name)

        self.platform_combo.currentIndexChanged.connect(self.on_platform_changed)
        platform_layout.addWidget(platform_label)
        platform_layout.addWidget(self.platform_combo, 1)
        source_layout.addLayout(platform_layout)

        # Campo URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        url_label.setMinimumWidth(90)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Pega aquí la URL del contenido...")
        self.url_input.textChanged.connect(self.on_url_changed)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        source_layout.addLayout(url_layout)

        # Indicador de plataforma detectada
        self.detected_platform_label = QLabel("")
        self.detected_platform_label.setStyleSheet(f"color: {MATRIX_COLORS['text_dim']}; font-size: 9pt; padding-left: 95px;")
        source_layout.addWidget(self.detected_platform_label)

        source_group.setLayout(source_layout)
        main_layout.addWidget(source_group)
        
        # Grupo: Opciones de descarga
        options_group = QGroupBox(">> OPCIONES")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)

        # Formato
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        format_label.setMinimumWidth(90)
        self.format_video = QRadioButton("Video (MP4)")
        self.format_audio = QRadioButton("Audio (MP3)")
        # Por defecto: Audio (MP3)
        default_format = self.app_settings.get_default_format()
        if default_format == 'audio':
            self.format_audio.setChecked(True)
        else:
            self.format_video.setChecked(True)

        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_video)
        format_layout.addWidget(self.format_audio)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)

        # Calidad (solo para vídeo)
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Calidad:")
        quality_label.setMinimumWidth(90)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(VIDEO_QUALITIES)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo, 1)
        quality_layout.addStretch(2)
        options_layout.addLayout(quality_layout)

        # Opción de transcripción (solo para audio)
        transcription_layout = QHBoxLayout()
        transcription_label = QLabel("Extra:")
        transcription_label.setMinimumWidth(90)
        self.transcription_checkbox = QCheckBox("Generar transcripción (TXT)")
        self.transcription_checkbox.setToolTip("Genera un archivo de texto con la transcripción del audio usando IA")
        self.transcription_checkbox.setEnabled(self.format_audio.isChecked())
        transcription_layout.addWidget(transcription_label)
        transcription_layout.addWidget(self.transcription_checkbox)
        transcription_layout.addStretch()
        options_layout.addLayout(transcription_layout)

        # Mensaje de capacidades de plataforma
        self.platform_capabilities_label = QLabel("")
        self.platform_capabilities_label.setStyleSheet(f"color: {MATRIX_COLORS['warning']}; font-size: 9pt; padding-left: 95px;")
        options_layout.addWidget(self.platform_capabilities_label)

        # Mensaje de transcripción
        self.transcription_info_label = QLabel("")
        self.transcription_info_label.setStyleSheet(f"color: {MATRIX_COLORS['info']}; font-size: 9pt; padding-left: 95px;")
        options_layout.addWidget(self.transcription_info_label)

        options_group.setLayout(options_layout)
        main_layout.addWidget(options_group)
        
        # Pestañas para destino local/remoto
        destination_tabs = QTabWidget()
        
        # Pestaña: Destino Local
        local_tab = QWidget()
        local_layout = QVBoxLayout()
        local_layout.setContentsMargins(10, 10, 10, 10)
        local_layout.setSpacing(10)
        
        local_folder_group = QGroupBox(">> CARPETA LOCAL")
        local_folder_layout = QHBoxLayout()
        local_folder_layout.setContentsMargins(10, 10, 10, 10)
        
        self.local_folder_input = QLineEdit()
        self.local_folder_input.setPlaceholderText("Selecciona la carpeta donde guardar el archivo...")
        # Cargar última carpeta usada o usar la predeterminada
        last_local_folder = self.app_settings.get_last_local_folder()
        self.local_folder_input.setText(last_local_folder or DEFAULT_DOWNLOAD_FOLDER)
        # Guardar automáticamente cuando el usuario termine de editar
        self.local_folder_input.editingFinished.connect(self.save_local_folder)
        
        local_folder_button = QPushButton("📂 Buscar...")
        local_folder_button.clicked.connect(self.select_local_folder)
        
        local_folder_layout.addWidget(self.local_folder_input)
        local_folder_layout.addWidget(local_folder_button)
        
        local_folder_group.setLayout(local_folder_layout)
        local_layout.addWidget(local_folder_group)
        local_tab.setLayout(local_layout)

        # Fijar altura máxima del local_tab basada en su contenido
        local_tab.setMaximumHeight(100)
        
        # Pestaña: Destino SSH
        ssh_tab = QWidget()
        ssh_layout = QVBoxLayout()
        ssh_layout.setContentsMargins(10, 10, 10, 10)
        ssh_layout.setSpacing(10)
        
        # Configuraciones guardadas
        ssh_saved_group = QGroupBox(">> CONFIGURACIONES GUARDADAS")
        ssh_saved_layout = QHBoxLayout()
        ssh_saved_layout.setContentsMargins(10, 10, 10, 10)
        
        self.ssh_config_combo = QComboBox()
        self.ssh_config_combo.setPlaceholderText("Selecciona una configuración guardada...")
        self.ssh_config_combo.currentTextChanged.connect(self.load_ssh_config)
        ssh_saved_layout.addWidget(QLabel("Configuración:"))
        ssh_saved_layout.addWidget(self.ssh_config_combo)
        
        ssh_load_button = QPushButton("📥 Cargar")
        ssh_load_button.clicked.connect(self.load_selected_ssh_config)
        ssh_saved_layout.addWidget(ssh_load_button)
        
        ssh_save_button = QPushButton("Guardar")
        ssh_save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATRIX_COLORS['accent_dark']};
                color: {MATRIX_COLORS['text_bright']};
                border: 1px solid {MATRIX_COLORS['accent']};
            }}
            QPushButton:hover {{
                background-color: {MATRIX_COLORS['accent']};
            }}
        """)
        ssh_save_button.clicked.connect(self.save_current_ssh_config)
        ssh_saved_layout.addWidget(ssh_save_button)
        
        ssh_saved_group.setLayout(ssh_saved_layout)
        ssh_layout.addWidget(ssh_saved_group)
        
        # Configuración SSH
        ssh_config_group = QGroupBox(">> CONEXION SSH")
        ssh_config_layout = QFormLayout()
        ssh_config_layout.setContentsMargins(10, 15, 10, 10)
        ssh_config_layout.setSpacing(8)
        
        self.ssh_name_input = QLineEdit()
        self.ssh_name_input.setPlaceholderText("Nombre para esta configuración (ej: Servidor Casa)")
        ssh_config_layout.addRow("Nombre:", self.ssh_name_input)
        
        self.ssh_host_input = QLineEdit()
        self.ssh_host_input.setPlaceholderText("ejemplo: 192.168.1.100 o servidor.com")
        ssh_config_layout.addRow("Host:", self.ssh_host_input)
        
        self.ssh_port_input = QLineEdit()
        self.ssh_port_input.setPlaceholderText("22")
        self.ssh_port_input.setText("22")
        ssh_config_layout.addRow("Puerto:", self.ssh_port_input)
        
        self.ssh_user_input = QLineEdit()
        self.ssh_user_input.setPlaceholderText("usuario")
        ssh_config_layout.addRow("Usuario:", self.ssh_user_input)
        
        self.ssh_password_input = QLineEdit()
        self.ssh_password_input.setPlaceholderText("contraseña (opcional si usas clave)")
        self.ssh_password_input.setEchoMode(QLineEdit.Password)
        ssh_config_layout.addRow("Contraseña:", self.ssh_password_input)
        
        self.ssh_key_input = QLineEdit()
        self.ssh_key_input.setPlaceholderText("ruta a clave privada (opcional)")
        ssh_key_layout = QHBoxLayout()
        ssh_key_layout.addWidget(self.ssh_key_input)
        ssh_key_button = QPushButton("📄 Buscar...")
        ssh_key_button.clicked.connect(self.select_ssh_key)
        ssh_key_layout.addWidget(ssh_key_button)
        ssh_config_layout.addRow("Clave SSH:", ssh_key_layout)
        
        ssh_config_group.setLayout(ssh_config_layout)
        ssh_layout.addWidget(ssh_config_group)
        
        # Carpeta remota
        ssh_folder_group = QGroupBox(">> CARPETA REMOTA")
        ssh_folder_layout = QVBoxLayout()
        ssh_folder_layout.setContentsMargins(10, 10, 10, 10)
        ssh_folder_layout.setSpacing(8)
        
        # Layout horizontal para el campo y botón explorar
        folder_input_layout = QHBoxLayout()
        self.ssh_folder_input = QLineEdit()
        self.ssh_folder_input.setPlaceholderText("ejemplo: /home/usuario/Descargas")
        # Cargar última carpeta remota usada
        last_remote_folder = self.app_settings.get_last_remote_folder()
        if last_remote_folder:
            self.ssh_folder_input.setText(last_remote_folder)
        # Guardar automáticamente cuando el usuario termine de editar
        self.ssh_folder_input.editingFinished.connect(self.save_ssh_folder)
        folder_input_layout.addWidget(self.ssh_folder_input)
        
        ssh_browse_button = QPushButton("Explorar...")
        ssh_browse_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATRIX_COLORS['background_tertiary']};
                color: {MATRIX_COLORS['info']};
                border: 1px solid {MATRIX_COLORS['info']};
            }}
            QPushButton:hover {{
                background-color: #003344;
                color: #00EEFF;
            }}
        """)
        ssh_browse_button.clicked.connect(self.browse_ssh_folder)
        folder_input_layout.addWidget(ssh_browse_button)
        
        ssh_folder_layout.addLayout(folder_input_layout)
        
        ssh_test_button = QPushButton("Probar Conexion")
        ssh_test_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATRIX_COLORS['background_tertiary']};
                color: {MATRIX_COLORS['info']};
                border: 1px solid {MATRIX_COLORS['info']};
            }}
            QPushButton:hover {{
                background-color: #003344;
                color: #00EEFF;
            }}
        """)
        ssh_test_button.clicked.connect(self.test_ssh_connection)
        ssh_folder_layout.addWidget(ssh_test_button)
        
        # Botón para limpiar campos
        ssh_clear_button = QPushButton("Limpiar Campos")
        ssh_clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATRIX_COLORS['background_tertiary']};
                color: {MATRIX_COLORS['warning']};
                border: 1px solid {MATRIX_COLORS['warning']};
            }}
            QPushButton:hover {{
                background-color: #332200;
                color: #FFCC00;
            }}
        """)
        ssh_clear_button.clicked.connect(self.clear_ssh_fields)
        ssh_folder_layout.addWidget(ssh_clear_button)
        
        ssh_folder_group.setLayout(ssh_folder_layout)
        ssh_layout.addWidget(ssh_folder_group)
        ssh_layout.addStretch()  # Añadir stretch para que no ocupe más espacio del necesario
        ssh_tab.setLayout(ssh_layout)
        
        # Añadir pestañas
        destination_tabs.addTab(local_tab, "LOCAL")
        destination_tabs.addTab(ssh_tab, "SSH")

        # Configurar para que ajuste altura según contenido
        destination_tabs.setSizePolicy(
            destination_tabs.sizePolicy().horizontalPolicy(),
            destination_tabs.sizePolicy().verticalPolicy()
        )

        # Conectar cambio de pestaña
        destination_tabs.currentChanged.connect(self.on_tab_changed)

        self.destination_tabs = destination_tabs
        self.local_tab = local_tab
        self.ssh_tab = ssh_tab

        # Altura inicial para pestaña Local
        destination_tabs.setFixedHeight(120)

        main_layout.addWidget(destination_tabs)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p% - %v")
        main_layout.addWidget(self.progress_bar)
        
        # Mensaje de estado
        self.status_label = QLabel(">> SISTEMA LISTO")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {MATRIX_COLORS['accent']}; padding: 8px; font-family: 'Consolas', monospace;")
        main_layout.addWidget(self.status_label)
        
        # Área de mensajes
        messages_group = QGroupBox(">> LOG")
        messages_layout = QVBoxLayout()
        
        self.messages_text = QTextEdit()
        self.messages_text.setReadOnly(True)
        self.messages_text.setMaximumHeight(120)
        messages_layout.addWidget(self.messages_text)
        
        messages_group.setLayout(messages_layout)
        main_layout.addWidget(messages_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.download_button = QPushButton(">> DESCARGAR")
        self.download_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATRIX_COLORS['accent_dark']};
                color: {MATRIX_COLORS['text_bright']};
                font-weight: bold;
                padding: 14px 40px;
                font-size: 13pt;
                border: 2px solid {MATRIX_COLORS['accent']};
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                background-color: {MATRIX_COLORS['accent']};
                color: {MATRIX_COLORS['background']};
            }}
            QPushButton:disabled {{
                background-color: {MATRIX_COLORS['background_tertiary']};
                color: {MATRIX_COLORS['border_dim']};
                border: 2px solid {MATRIX_COLORS['border_dim']};
            }}
        """)
        self.download_button.clicked.connect(self.start_download)
        
        self.clear_button = QPushButton("LIMPIAR LOG")
        self.clear_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {MATRIX_COLORS['background_tertiary']};
                color: {MATRIX_COLORS['error']};
                border: 1px solid {MATRIX_COLORS['error']};
            }}
            QPushButton:hover {{
                background-color: #330011;
                color: #FF3366;
            }}
        """)
        self.clear_button.clicked.connect(self.clear_messages)
        
        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addStretch()
        
        main_layout.addLayout(buttons_layout)
        
        # Asegurar que el texto del botón sea correcto según la pestaña inicial
        self.on_tab_changed(0)  # Inicializar con pestaña Local
        
        # Conectar cambio de formato para habilitar/deshabilitar calidad
        self.format_video.toggled.connect(self.on_format_changed)
        self.format_audio.toggled.connect(self.on_format_changed)
    
    def on_format_changed(self):
        """Habilita o deshabilita el selector de calidad y transcripción según el formato"""
        is_video = self.format_video.isChecked()
        is_audio = self.format_audio.isChecked()

        self.quality_combo.setEnabled(is_video)
        self.transcription_checkbox.setEnabled(is_audio)

        if is_video:
            self.transcription_checkbox.setChecked(False)
            self.transcription_info_label.setText("")
        else:
            self.transcription_info_label.setText("La transcripción usa Whisper AI (puede tardar)")
    
    def on_tab_changed(self, index):
        """Se ejecuta cuando se cambia de pestaña"""
        # Actualizar texto del botón de descargar según la pestaña activa
        if index == 1:  # Pestaña SSH
            self.download_button.setText(">> DESCARGAR + SSH")
            self.destination_tabs.setFixedHeight(420)
        else:  # Pestaña Local (índice 0)
            self.download_button.setText(">> DESCARGAR")
            self.destination_tabs.setFixedHeight(120)

    def on_platform_changed(self, index):
        """Se ejecuta cuando se cambia la plataforma seleccionada"""
        platform = self.platform_combo.currentData()
        if platform and platform in SUPPORTED_PLATFORMS:
            capabilities = SUPPORTED_PLATFORMS[platform]

            # Actualizar opciones de formato según capacidades
            if not capabilities["supports_video"]:
                self.format_audio.setChecked(True)
                self.format_video.setEnabled(False)
                self.quality_combo.setEnabled(False)
                self.platform_capabilities_label.setText("Esta plataforma solo soporta audio")
            elif not capabilities["supports_audio"]:
                self.format_video.setChecked(True)
                self.format_audio.setEnabled(False)
                self.quality_combo.setEnabled(True)
                self.platform_capabilities_label.setText("Esta plataforma solo soporta video")
            else:
                self.format_video.setEnabled(True)
                self.format_audio.setEnabled(True)
                self.quality_combo.setEnabled(self.format_video.isChecked())
                self.platform_capabilities_label.setText("")

    def on_url_changed(self, text):
        """Se ejecuta cuando cambia la URL para detectar plataforma automáticamente"""
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
    
    def save_local_folder(self):
        """Guarda la carpeta local actual como predeterminada"""
        folder = self.local_folder_input.text().strip()
        if folder:
            self.app_settings.set_last_local_folder(folder)
    
    def select_local_folder(self):
        """Abre un diálogo para seleccionar la carpeta de destino local"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta de Destino",
            self.local_folder_input.text()
        )
        if folder:
            self.local_folder_input.setText(folder)
            # Guardar última carpeta usada (también se guardará por editingFinished)
            self.app_settings.set_last_local_folder(folder)
    
    def select_ssh_key(self):
        """Abre un diálogo para seleccionar el archivo de clave SSH"""
        key_file, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Clave SSH",
            str(Path.home() / ".ssh"),
            "Claves SSH (*);;Todos los archivos (*)"
        )
        if key_file:
            self.ssh_key_input.setText(key_file)
    
    def initialize_default_ssh_config(self):
        """Inicializa la configuración SSH predeterminada si no existe"""
        # Esta función ya no crea configuraciones predeterminadas con datos sensibles
        # Los usuarios deben configurar sus propios servidores manualmente
        pass
    
    def load_saved_ssh_configs(self):
        """Carga las configuraciones SSH guardadas en el ComboBox"""
        configs = self.config_manager.load_configs()
        self.ssh_config_combo.clear()
        self.ssh_config_combo.addItem("-- Nueva configuración --", None)
        for config in configs:
            name = config.get('name', 'Sin nombre')
            self.ssh_config_combo.addItem(name, config)
        
        # Si hay configuraciones, seleccionar "Servidor Casa" si existe
        for i in range(self.ssh_config_combo.count()):
            if self.ssh_config_combo.itemText(i) == "Servidor Casa":
                self.ssh_config_combo.setCurrentIndex(i)
                break
    
    def load_ssh_config(self, text):
        """Carga una configuración SSH cuando se selecciona del ComboBox"""
        if text == "-- Nueva configuración --":
            return
        
        # Obtener la configuración del índice seleccionado
        index = self.ssh_config_combo.currentIndex()
        if index > 0:  # El índice 0 es "-- Nueva configuración --"
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
    
    def load_selected_ssh_config(self):
        """Carga la configuración SSH seleccionada"""
        self.load_ssh_config(self.ssh_config_combo.currentText())
    
    def clear_ssh_fields(self):
        """Limpia todos los campos SSH"""
        self.ssh_name_input.setText("")
        self.ssh_host_input.setText("")
        self.ssh_port_input.setText("22")
        self.ssh_user_input.setText("")
        self.ssh_password_input.setText("")
        self.ssh_key_input.setText("")
        self.ssh_folder_input.setText("")
        self.add_message("Campos SSH limpiados", "info")
    
    def save_current_ssh_config(self):
        """Guarda la configuración SSH actual"""
        name = self.ssh_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Por favor, introduce un nombre para la configuración")
            return
        
        host = self.ssh_host_input.text().strip()
        if not host:
            QMessageBox.warning(self, "Error", "Por favor, introduce el host del servidor")
            return
        
        try:
            port = int(self.ssh_port_input.text().strip() or "22")
        except ValueError:
            QMessageBox.warning(self, "Error", "El puerto debe ser un número")
            return
        
        username = self.ssh_user_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Por favor, introduce el usuario")
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
            self.add_message(f"✅ Configuración '{name}' guardada correctamente", "success")
            self.load_saved_ssh_configs()
            # Seleccionar la configuración guardada
            index = self.ssh_config_combo.findText(name)
            if index >= 0:
                self.ssh_config_combo.setCurrentIndex(index)
            QMessageBox.information(self, "Éxito", f"Configuración '{name}' guardada correctamente")
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar la configuración")
    
    def get_ssh_config_dict(self):
        """Obtiene la configuración SSH actual como diccionario"""
        try:
            return {
                'host': self.ssh_host_input.text().strip(),
                'port': int(self.ssh_port_input.text().strip() or "22"),
                'username': self.ssh_user_input.text().strip(),
                'password': self.ssh_password_input.text().strip() or None,
                'key_file': self.ssh_key_input.text().strip() or None
            }
        except ValueError:
            return None
    
    def browse_ssh_folder(self):
        """Abre el explorador de carpetas SSH"""
        if not self.validate_ssh_inputs():
            QMessageBox.warning(
                self, 
                "Error", 
                "Por favor, completa la configuración SSH (Host y Usuario) antes de explorar"
            )
            return
        
        ssh_config = self.get_ssh_config_dict()
        if not ssh_config:
            QMessageBox.warning(self, "Error", "Error en la configuración SSH. Verifica el puerto.")
            return
        
        # Abrir diálogo de explorador
        browser = SSHBrowserDialog(self, ssh_config)
        
        if browser.exec() == QDialog.Accepted:
            selected_path = browser.get_selected_path()
            if selected_path:
                self.ssh_folder_input.setText(selected_path)
                # Guardar última carpeta remota usada (también se guardará por editingFinished)
                self.app_settings.set_last_remote_folder(selected_path)
                self.add_message(f"✅ Carpeta seleccionada: {selected_path}", "success")
    
    def save_ssh_folder(self):
        """Guarda la carpeta SSH actual como predeterminada"""
        folder = self.ssh_folder_input.text().strip()
        if folder:
            self.app_settings.set_last_remote_folder(folder)
    
    def test_ssh_connection(self):
        """Prueba la conexión SSH"""
        if not self.validate_ssh_inputs():
            return
        
        self.add_message("Probando conexión SSH...", "info")
        
        try:
            ssh_client = SSHClient()
            host = self.ssh_host_input.text().strip()
            port = int(self.ssh_port_input.text().strip() or "22")
            username = self.ssh_user_input.text().strip()
            password = self.ssh_password_input.text().strip() or None
            key_file = self.ssh_key_input.text().strip() or None
            
            success, message = ssh_client.connect(host, port, username, password, key_file)
            
            if success:
                # Probar conexión
                test_success, test_msg = ssh_client.test_connection()
                ssh_client.disconnect()
                
                if test_success:
                    self.add_message("✅ Conexión SSH exitosa!", "success")
                    QMessageBox.information(self, "Conexión Exitosa", "La conexión SSH se estableció correctamente.")
                else:
                    self.add_message(f"⚠️ {test_msg}", "warning")
            else:
                self.add_message(f"❌ Error de conexión: {message}", "error")
                QMessageBox.warning(self, "Error de Conexión", message)
        
        except ValueError:
            self.add_message("❌ El puerto debe ser un número", "error")
        except Exception as e:
            self.add_message(f"❌ Error: {str(e)}", "error")
    
    def validate_ssh_inputs(self):
        """Valida los campos de entrada SSH"""
        if not self.ssh_host_input.text().strip():
            QMessageBox.warning(self, "Error", "Por favor, introduce el host del servidor SSH")
            return False
        
        if not self.ssh_user_input.text().strip():
            QMessageBox.warning(self, "Error", "Por favor, introduce el usuario SSH")
            return False
        
        try:
            port = self.ssh_port_input.text().strip()
            if port and (int(port) < 1 or int(port) > 65535):
                QMessageBox.warning(self, "Error", "El puerto debe estar entre 1 y 65535")
                return False
        except ValueError:
            QMessageBox.warning(self, "Error", "El puerto debe ser un número")
            return False
        
        return True
    
    def add_message(self, message, message_type="info"):
        """
        Añade un mensaje al área de mensajes

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
        self.messages_text.append(f'<span style="color: {color}; font-weight: bold;">[{message_type.upper()}]</span> <span style="color: {MATRIX_COLORS["text"]};">{message}</span>')
    
    def clear_messages(self):
        """Limpia el área de mensajes"""
        self.messages_text.clear()
    
    def validate_inputs(self):
        """
        Valida los campos de entrada

        Returns:
            bool: True si los campos son válidos
        """
        url = self.url_input.text().strip()
        platform = self.platform_combo.currentData()

        if not url:
            QMessageBox.warning(self, "Error", "Por favor, introduce una URL")
            return False

        # Validar URL según la plataforma seleccionada
        is_valid, error_msg = InputValidator.validate_url(url, platform)
        if not is_valid:
            QMessageBox.warning(self, "Error de Validación", error_msg)
            return False
        
        # Validar destino según la pestaña seleccionada
        if self.destination_tabs.currentIndex() == 0:  # Local
            folder = self.local_folder_input.text().strip()
            is_valid, error_msg = InputValidator.validate_folder(folder)
            if not is_valid:
                QMessageBox.warning(self, "Error de Validación", error_msg)
                return False
        else:  # SSH
            if not self.validate_ssh_inputs():
                return False
            if not self.ssh_folder_input.text().strip():
                QMessageBox.warning(self, "Error", "Por favor, introduce la carpeta de destino remota")
                return False
        
        return True
    
    def download_video(self, url, output_folder, is_audio, quality, use_ssh=False, ssh_config=None, transcribe=False):
        """
        Descarga el vídeo en un hilo separado

        Args:
            url: URL del vídeo
            output_folder: Carpeta de destino
            is_audio: True si es solo audio
            quality: Calidad del vídeo
            use_ssh: True si se debe subir a servidor SSH
            ssh_config: Diccionario con configuración SSH
            transcribe: True si se debe transcribir el audio
        """
        temp_file = None
        try:
            # Obtener información del vídeo
            info = YouTubeDownloader.get_video_info(url)
            video_title = info.get('title', 'Video')
            
            self.progress_hook.progress.emit(0, f"Iniciando descarga: {video_title}")
            self.download_signals.message.emit(f"Iniciando descarga: {video_title}", "info")
            
            if use_ssh:
                # Descargar a carpeta temporal primero
                temp_dir = tempfile.gettempdir()
                temp_output_dir = os.path.join(temp_dir, "youtube_download")
                os.makedirs(temp_output_dir, exist_ok=True)
                
                # Obtener lista de archivos antes de descargar
                files_before = set()
                if os.path.exists(temp_output_dir):
                    files_before = set(os.listdir(temp_output_dir))
                
                # Para audio, usar solo el directorio (yt-dlp generará el nombre)
                if is_audio:
                    # Usar template de yt-dlp para que genere el nombre correcto
                    temp_output = os.path.join(temp_output_dir, "%(title)s.%(ext)s")
                else:
                    temp_output = os.path.join(temp_output_dir, f"{video_title}.mp4")
                
                self.download_signals.message.emit("Descargando a carpeta temporal...", "info")
                success, message, title = YouTubeDownloader.download(
                    url, temp_output, is_audio, quality, self.progress_hook
                )
                
                if success:
                    # Esperar un momento para que se complete la escritura del archivo
                    import time
                    time.sleep(1)
                    
                    # Buscar el archivo real (yt-dlp puede cambiar el nombre y extensión)
                    actual_file = None
                    
                    if os.path.exists(temp_output_dir):
                        # Obtener lista de archivos después de la descarga
                        files_after = set(os.listdir(temp_output_dir))
                        new_files = files_after - files_before
                        
                        if new_files:
                            # Filtrar por extensión correcta
                            if is_audio:
                                mp3_files = [f for f in new_files if f.endswith('.mp3')]
                                if mp3_files:
                                    # Tomar el archivo más reciente que sea .mp3
                                    actual_file = max(
                                        [os.path.join(temp_output_dir, f) for f in mp3_files],
                                        key=os.path.getmtime
                                    )
                            else:
                                mp4_files = [f for f in new_files if f.endswith('.mp4')]
                                if mp4_files:
                                    actual_file = max(
                                        [os.path.join(temp_output_dir, f) for f in mp4_files],
                                        key=os.path.getmtime
                                    )
                            
                            # Si no se encontró con la extensión correcta, tomar el más reciente
                            if not actual_file:
                                actual_file = max(
                                    [os.path.join(temp_output_dir, f) for f in new_files],
                                    key=os.path.getmtime
                                )
                    
                    # Si aún no se encuentra, buscar cualquier archivo que contenga el título
                    if not actual_file or not os.path.exists(actual_file):
                        if os.path.exists(temp_output_dir):
                            # Buscar archivos que contengan parte del título
                            title_words = video_title.split()[:3]  # Primeras 3 palabras
                            for file in os.listdir(temp_output_dir):
                                file_path = os.path.join(temp_output_dir, file)
                                if os.path.isfile(file_path):
                                    # Verificar si el archivo contiene palabras del título
                                    if any(word.lower() in file.lower() for word in title_words if len(word) > 3):
                                        if is_audio and file.endswith('.mp3'):
                                            actual_file = file_path
                                            break
                                        elif not is_audio and file.endswith('.mp4'):
                                            actual_file = file_path
                                            break
                    
                    # Último recurso: tomar el archivo más reciente del directorio
                    if not actual_file or not os.path.exists(actual_file):
                        if os.path.exists(temp_output_dir):
                            all_files = [
                                os.path.join(temp_output_dir, f) 
                                for f in os.listdir(temp_output_dir) 
                                if os.path.isfile(os.path.join(temp_output_dir, f))
                            ]
                            if all_files:
                                actual_file = max(all_files, key=os.path.getmtime)
                    
                    if not actual_file or not os.path.exists(actual_file):
                        # Listar archivos para debug
                        debug_files = os.listdir(temp_output_dir) if os.path.exists(temp_output_dir) else []
                        raise Exception(f"No se pudo encontrar el archivo descargado. Archivos en directorio: {debug_files}")
                    
                    # Verificar que el archivo tiene contenido
                    file_size = os.path.getsize(actual_file)
                    if file_size == 0:
                        raise Exception(f"El archivo descargado está vacío: {actual_file}")
                    
                    file_size = os.path.getsize(actual_file)
                    self.download_signals.message.emit(
                        f"Archivo descargado: {os.path.basename(actual_file)} ({file_size / 1024 / 1024:.2f} MB)", 
                        "info"
                    )
                    
                    self.download_signals.message.emit("Conectando al servidor SSH...", "info")
                    self.progress_hook.progress.emit(60, "Conectando al servidor...")
                    
                    # Conectar SSH
                    ssh_client = SSHClient()
                    conn_success, conn_msg = ssh_client.connect(
                        ssh_config['host'],
                        ssh_config['port'],
                        ssh_config['username'],
                        ssh_config.get('password'),
                        ssh_config.get('key_file')
                    )
                    
                    if not conn_success:
                        raise Exception(f"Error de conexión SSH: {conn_msg}")
                    
                    self.download_signals.message.emit("✅ Conexión SSH establecida", "success")
                    
                    # Verificar que la carpeta remota existe y tiene permisos
                    self.download_signals.message.emit("Verificando carpeta remota...", "info")
                    stdin, stdout, stderr = ssh_client.client.exec_command(
                        f'test -d "{ssh_config["remote_folder"]}" && test -w "{ssh_config["remote_folder"]}" && echo "OK" || echo "ERROR"'
                    )
                    folder_check = stdout.read().decode().strip()
                    
                    if folder_check != "OK":
                        # Intentar crear la carpeta
                        create_success, create_msg = ssh_client.create_directory(ssh_config['remote_folder'])
                        if not create_success:
                            raise Exception(f"No se puede acceder a la carpeta remota: {create_msg}")
                    
                    self.download_signals.message.emit("Subiendo archivo al servidor...", "info")
                    self.progress_hook.progress.emit(70, "Subiendo archivo...")
                    
                    # Subir archivo - usar el nombre del archivo real
                    remote_filename = os.path.basename(actual_file)
                    remote_path = os.path.join(ssh_config['remote_folder'], remote_filename)
                    
                    file_size_mb = os.path.getsize(actual_file) / 1024 / 1024
                    self.download_signals.message.emit(
                        f"Subiendo {remote_filename} ({file_size_mb:.2f} MB) a {ssh_config['remote_folder']}...", 
                        "info"
                    )
                    
                    # Subir archivo con timeout
                    upload_success, upload_msg = ssh_client.upload_file(actual_file, remote_path)
                    
                    if upload_success:
                        self.download_signals.message.emit(f"✅ {upload_msg}", "success")
                    else:
                        self.download_signals.message.emit(f"❌ {upload_msg}", "error")
                    
                    ssh_client.disconnect()
                    
                    if upload_success:
                        # Guardar carpeta remota usada después de descarga exitosa
                        if ssh_config and ssh_config.get('remote_folder'):
                            self.app_settings.set_last_remote_folder(ssh_config['remote_folder'])
                        
                        # Eliminar archivo temporal
                        try:
                            os.remove(actual_file)
                            # Limpiar directorio temporal si está vacío
                            try:
                                if not os.listdir(temp_output_dir):
                                    os.rmdir(temp_output_dir)
                            except:
                                pass
                        except Exception as e:
                            self.download_signals.message.emit(
                                f"⚠️ No se pudo eliminar archivo temporal: {str(e)}", 
                                "warning"
                            )
                        
                        self.progress_hook.progress.emit(100, "¡Descarga y subida completadas!")
                        self.download_signals.message.emit(f"¡Archivo subido exitosamente a: {remote_path}!", "success")
                        self.download_signals.download_finished.emit(
                            True,
                            f"¡Descarga y subida completadas!\n\n{title}\n\nGuardado en servidor: {remote_path}",
                            title
                        )
                    else:
                        raise Exception(f"Error al subir archivo: {upload_msg}")
                else:
                    raise Exception(message)
            else:
                # Descarga local normal
                success, message, title = YouTubeDownloader.download(
                    url, output_folder, is_audio, quality, self.progress_hook
                )

                if success:
                    # Guardar carpeta local usada después de descarga exitosa
                    if output_folder:
                        self.app_settings.set_last_local_folder(output_folder)

                    transcription_result = ""

                    # Transcribir si está habilitado y es audio
                    if is_audio and transcribe:
                        self.progress_hook.progress.emit(95, "Transcribiendo audio...")
                        self.download_signals.message.emit("Iniciando transcripción con Whisper AI...", "info")

                        # Buscar el archivo de audio descargado
                        import glob
                        import time
                        time.sleep(1)  # Esperar a que se complete la escritura

                        # Buscar archivos MP3 recientes en la carpeta
                        mp3_files = glob.glob(os.path.join(output_folder, "*.mp3"))
                        if mp3_files:
                            audio_file = max(mp3_files, key=os.path.getmtime)

                            # Generar nombre para el archivo de transcripción
                            txt_filename = os.path.splitext(audio_file)[0] + "_transcripcion.txt"

                            # Transcribir
                            trans_success, trans_msg, trans_text = AudioTranscriber.transcribe(
                                audio_file,
                                txt_filename,
                                model_name="base",
                                language="es"
                            )

                            if trans_success:
                                self.download_signals.message.emit(f"Transcripción guardada: {os.path.basename(txt_filename)}", "success")
                                transcription_result = f"\nTranscripción: {txt_filename}"
                            else:
                                self.download_signals.message.emit(f"Error en transcripción: {trans_msg}", "warning")
                                transcription_result = f"\nTranscripción fallida: {trans_msg}"
                        else:
                            self.download_signals.message.emit("No se encontró archivo de audio para transcribir", "warning")

                    self.progress_hook.progress.emit(100, "¡Descarga completada!")
                    self.download_signals.message.emit(
                        f"¡Descarga completada! Archivo guardado en: {output_folder}",
                        "success"
                    )
                    self.download_signals.download_finished.emit(
                        True,
                        f"¡Descarga completada!\n\n{title}\n\nGuardado en: {output_folder}{transcription_result}",
                        title
                    )
                else:
                    raise Exception(message)
        
        except Exception as e:
            error_msg = str(e)
            self.progress_hook.progress.emit(0, f"Error: {error_msg}")
            self.download_signals.message.emit(f"Error en la descarga: {error_msg}", "error")
            self.download_signals.download_finished.emit(False, f"Error al descargar el vídeo:\n\n{error_msg}", "")
        
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
    
    def start_download(self):
        """Inicia el proceso de descarga"""
        if not self.validate_inputs():
            return
        
        # Deshabilitar botón durante la descarga
        self.download_button.setEnabled(False)
        self.status_label.setText(">> DESCARGANDO...")
        self.progress_bar.setValue(0)
        
        # Crear hook de progreso
        self.progress_hook = DownloadProgressHook()
        self.progress_hook.progress.connect(self.update_progress)
        
        # Obtener parámetros
        url = self.url_input.text().strip()
        is_audio = self.format_audio.isChecked()
        quality = self.quality_combo.currentText() if not is_audio else None
        transcribe = self.transcription_checkbox.isChecked() and is_audio

        # Guardar formato por defecto
        format_type = 'audio' if is_audio else 'video'
        self.app_settings.set_default_format(format_type)

        # Determinar destino
        use_ssh = self.destination_tabs.currentIndex() == 1  # SSH tab

        if use_ssh:
            output_folder = self.ssh_folder_input.text().strip()
            # Guardar última carpeta remota usada
            if output_folder:
                self.app_settings.set_last_remote_folder(output_folder)
            ssh_config = {
                'host': self.ssh_host_input.text().strip(),
                'port': int(self.ssh_port_input.text().strip() or "22"),
                'username': self.ssh_user_input.text().strip(),
                'password': self.ssh_password_input.text().strip() or None,
                'key_file': self.ssh_key_input.text().strip() or None,
                'remote_folder': output_folder
            }
        else:
            output_folder = self.local_folder_input.text().strip()
            # Guardar última carpeta local usada
            if output_folder:
                self.app_settings.set_last_local_folder(output_folder)
            ssh_config = None

        # Iniciar descarga en hilo separado
        self.download_thread = Thread(
            target=self.download_video,
            args=(url, output_folder, is_audio, quality, use_ssh, ssh_config, transcribe)
        )
        self.download_thread.daemon = True
        self.download_thread.start()
    
    def update_progress(self, percent, message):
        """
        Actualiza la barra de progreso y el mensaje de estado

        Args:
            percent: Porcentaje de descarga (0-100)
            message: Mensaje de estado
        """
        self.progress_bar.setValue(percent)
        self.status_label.setText(f">> {message}")
