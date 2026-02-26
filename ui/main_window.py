#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana principal de la aplicacion.
Orquesta los widgets de ui/widgets/ y gestiona la descarga en hilo.
"""

import logging
import os
import tempfile
import time
import glob
import threading
from threading import Thread

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QScrollArea, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QFont, QShortcut, QKeySequence

from config import (
    APP_NAME, APP_VERSION,
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_X, WINDOW_Y,
    MATRIX_COLORS
)
from download.progress_hook import DownloadProgressHook, DownloadCancelled
from download.downloader import YouTubeDownloader
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


# ---------------------------------------------------------------------------
# Signals for thread-safe UI updates
# ---------------------------------------------------------------------------

class DownloadSignals(QObject):
    """Senales para comunicacion entre hilos"""
    message = Signal(str, str)              # mensaje, tipo
    progress_update = Signal(int, str)      # porcentaje, mensaje
    show_dialog = Signal(str, str, str)     # titulo, mensaje, tipo (info/error/warning)
    download_finished = Signal(bool, str, str)  # exito, mensaje, titulo


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class YouTubeDownloaderApp(QMainWindow):
    """Aplicacion principal para descargar contenido multimedia"""

    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.progress_hook = None
        self._cancel_event = threading.Event()

        # Managers
        self.config_manager = SSHConfigManager()
        self.app_settings = AppSettings()

        # Thread-safe signals
        self.download_signals = DownloadSignals()
        self.download_signals.message.connect(self._on_signal_message)
        self.download_signals.progress_update.connect(self._on_signal_progress)
        self.download_signals.show_dialog.connect(self.show_dialog_safe)
        self.download_signals.download_finished.connect(self.on_download_finished)

        # Build UI
        self.init_ui()
        self.setStyleSheet(app_stylesheet())
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")

        # Load saved SSH configs
        self.ssh_tab.load_saved_configs()

        # Cleanup leftover temp files from previous sessions
        self._cleanup_temp_files()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setGeometry(WINDOW_X, WINDOW_Y, WINDOW_WIDTH + 100, WINDOW_HEIGHT + 100)

        # Scroll area wrapping the central widget
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        central_widget = QWidget()
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        # -- Title --
        title = QLabel(">> Media Downloader <<")
        title_font = QFont("Consolas", 24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {MATRIX_COLORS['accent']}; margin-bottom: 5px; font-weight: bold;"
        )
        main_layout.addWidget(title)

        # -- Subtitle --
        subtitle = QLabel(f"[ Multi-Platform Media Downloader v{APP_VERSION} ]")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(
            f"color: {MATRIX_COLORS['text_dim']}; font-size: 10pt; margin-bottom: 10px;"
        )
        main_layout.addWidget(subtitle)

        # -- Source widget (platform + URL) --
        self.source = SourceWidget()
        main_layout.addWidget(self.source)

        # -- Options widget (format, quality, transcription, whisper) --
        default_format = self.app_settings.get_default_format()
        self.options = OptionsWidget(default_format=default_format)
        main_layout.addWidget(self.options)

        # -- Destination tabs (Local / SSH) --
        self.destination_tabs = QTabWidget()

        self.local_tab = LocalTab(self.app_settings)
        self.ssh_tab = SSHTab(self.config_manager, self.app_settings)

        self.destination_tabs.addTab(self.local_tab, "LOCAL")
        self.destination_tabs.addTab(self.ssh_tab, "SSH")
        main_layout.addWidget(self.destination_tabs)

        # -- Progress widget (bar + status + log) --
        self.progress = ProgressWidget()
        main_layout.addWidget(self.progress)

        # -- Action buttons --
        buttons_layout = QHBoxLayout()

        self.download_button = QPushButton(">> DESCARGAR")
        self.download_button.setStyleSheet(download_button_style())
        self.download_button.clicked.connect(self.start_download)

        self.cancel_button = QPushButton("CANCELAR")
        self.cancel_button.setStyleSheet(cancel_button_style())
        self.cancel_button.clicked.connect(self.cancel_download)
        self.cancel_button.setVisible(False)

        buttons_layout.addWidget(self.download_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()

        main_layout.addLayout(buttons_layout)

        # -- Wire widget signals --
        self.source.platform_changed.connect(self.options.update_platform_capabilities)
        self.source.url_changed.connect(self._on_url_changed)
        self.ssh_tab.message.connect(self.progress.add_message)
        self.destination_tabs.currentChanged.connect(self._on_tab_changed)

        # Initial tab state — delay so widgets have valid sizeHints
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._on_tab_changed(0))

        # -- Keyboard shortcuts --
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.start_download)
        QShortcut(QKeySequence("Escape"), self, activated=self.cancel_download)

    # ------------------------------------------------------------------
    # Signal handlers / slot helpers
    # ------------------------------------------------------------------

    def _on_signal_message(self, message: str, msg_type: str):
        """Route download-thread messages to progress widget"""
        self.progress.add_message(message, msg_type)

    def _on_signal_progress(self, percent: int, message: str):
        """Route download-thread progress to progress widget"""
        self.progress.update_progress(percent, message)

    def _on_url_changed(self, text: str):
        """Validate URL visually as the user types"""
        url = text.strip()
        if not url:
            self.source.set_url_valid(None)
            return
        platform = self.source.get_platform()
        is_valid, _ = InputValidator.validate_url(url, platform)
        self.source.set_url_valid(is_valid)

    def _on_tab_changed(self, index: int):
        """Update download button text and adjust tab height when tab changes"""
        if index == 1:
            self.download_button.setText(">> DESCARGAR + SSH")
        else:
            self.download_button.setText(">> DESCARGAR")

        # Adjust QTabWidget height to fit the current tab content
        for i in range(self.destination_tabs.count()):
            widget = self.destination_tabs.widget(i)
            if i == index:
                widget.setSizePolicy(widget.sizePolicy().horizontalPolicy(),
                                     QSizePolicy.Preferred)
            else:
                widget.setSizePolicy(widget.sizePolicy().horizontalPolicy(),
                                     QSizePolicy.Ignored)
        self.destination_tabs.setFixedHeight(
            self.destination_tabs.currentWidget().sizeHint().height()
            + self.destination_tabs.tabBar().sizeHint().height() + 10
        )

    # ------------------------------------------------------------------
    # Download lifecycle
    # ------------------------------------------------------------------

    def start_download(self):
        """Validates inputs and starts the download in a background thread"""
        # Prevent double-start
        if self.download_thread and self.download_thread.is_alive():
            return

        # -- Validate URL --
        url = self.source.get_url()
        platform = self.source.get_platform()

        if not url:
            QMessageBox.warning(self, "Error", "Por favor, introduce una URL")
            return

        is_valid, error_msg = InputValidator.validate_url(url, platform)
        if not is_valid:
            QMessageBox.warning(self, "Error de Validacion", error_msg)
            return

        # -- Validate destination folder --
        use_ssh = self.destination_tabs.currentIndex() == 1

        if use_ssh:
            if not self.ssh_tab.validate_inputs():
                return
            remote_folder = self.ssh_tab.get_remote_folder()
            if not remote_folder:
                QMessageBox.warning(
                    self, "Error",
                    "Por favor, introduce la carpeta de destino remota"
                )
                return
            ssh_config = self.ssh_tab.get_config_dict()
            if not ssh_config:
                QMessageBox.warning(
                    self, "Error",
                    "Error en la configuracion SSH. Verifica el puerto."
                )
                return
            ssh_config['remote_folder'] = remote_folder
            output_folder = remote_folder
        else:
            output_folder = self.local_tab.get_folder()
            folder_ok, folder_err = InputValidator.validate_folder(output_folder)
            if not folder_ok:
                QMessageBox.warning(self, "Error de Validacion", folder_err)
                return
            ssh_config = None

        # -- Gather options --
        is_audio = self.options.is_audio()
        quality = self.options.get_quality() if not is_audio else None
        transcribe = self.options.should_transcribe()
        whisper_model = self.options.get_whisper_model()

        # -- UI feedback --
        self.download_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress.update_progress(0, "DESCARGANDO...")

        # -- Progress hook --
        self.progress_hook = DownloadProgressHook(cancel_event=self._cancel_event)
        self.progress_hook.progress.connect(self.progress.update_progress)

        # Reset cancel event
        self._cancel_event.clear()

        # -- Save format preference --
        fmt = 'audio' if is_audio else 'video'
        self.app_settings.set_default_format(fmt)

        # -- Launch thread --
        self.download_thread = Thread(
            target=self.download_video,
            args=(url, output_folder, is_audio, quality,
                  use_ssh, ssh_config, transcribe, whisper_model),
            daemon=True
        )
        self.download_thread.start()

    def cancel_download(self):
        """Signals the download thread to stop"""
        if not self._cancel_event.is_set():
            self._cancel_event.set()
            self.download_signals.message.emit("Cancelando descarga...", "warning")
            self.progress.update_progress(0, "CANCELADO")
            self.download_button.setEnabled(True)
            self.cancel_button.setVisible(False)

    # ------------------------------------------------------------------
    # Download logic (runs in background thread)
    # ------------------------------------------------------------------

    def download_video(self, url, output_folder, is_audio, quality,
                       use_ssh=False, ssh_config=None,
                       transcribe=False, whisper_model="base"):
        """
        Core download logic executed in a daemon thread.

        Handles: local download, SSH upload, and optional transcription.
        Checks self._cancel_event before every major phase.
        """
        temp_output_dir = None
        actual_file = None

        try:
            # ── Phase 0: get video info ─────────────────────────────
            if self._cancel_event.is_set():
                return

            info = YouTubeDownloader.get_video_info(url)
            video_title = info.get('title', 'Video')

            self.progress_hook.progress.emit(0, f"Iniciando descarga: {video_title}")
            self.download_signals.message.emit(
                f"Iniciando descarga: {video_title}", "info"
            )

            # ── Phase 1: download ──────────────────────────────────
            if self._cancel_event.is_set():
                return

            if use_ssh:
                # Download to a temp directory first
                temp_output_dir = os.path.join(
                    tempfile.gettempdir(), "youtube_download"
                )
                os.makedirs(temp_output_dir, exist_ok=True)

                files_before = set(os.listdir(temp_output_dir)) if os.path.exists(temp_output_dir) else set()

                if is_audio:
                    temp_output = os.path.join(temp_output_dir, "%(title)s.%(ext)s")
                else:
                    temp_output = os.path.join(temp_output_dir, f"{video_title}.mp4")

                self.download_signals.message.emit(
                    "Descargando a carpeta temporal...", "info"
                )
                success, message, title = YouTubeDownloader.download(
                    url, temp_output, is_audio, quality, self.progress_hook
                )

                if not success:
                    raise Exception(message)

                time.sleep(1)

                # Locate the downloaded file
                actual_file = self._find_downloaded_file(
                    temp_output_dir, files_before, is_audio, video_title
                )
                if not actual_file or not os.path.exists(actual_file):
                    debug_files = os.listdir(temp_output_dir) if os.path.exists(temp_output_dir) else []
                    raise Exception(
                        f"No se pudo encontrar el archivo descargado. "
                        f"Archivos en directorio: {debug_files}"
                    )

                file_size = os.path.getsize(actual_file)
                if file_size == 0:
                    raise Exception(f"El archivo descargado esta vacio: {actual_file}")

                self.download_signals.message.emit(
                    f"Archivo descargado: {os.path.basename(actual_file)} "
                    f"({file_size / 1024 / 1024:.2f} MB)",
                    "info"
                )

                # ── Phase 2: SSH connect ───────────────────────────
                if self._cancel_event.is_set():
                    self._remove_temp(actual_file, temp_output_dir)
                    return

                self.download_signals.message.emit(
                    "Conectando al servidor SSH...", "info"
                )
                self.progress_hook.progress.emit(60, "Conectando al servidor...")

                ssh_client = SSHClient()
                conn_ok, conn_msg = ssh_client.connect(
                    ssh_config['host'],
                    ssh_config['port'],
                    ssh_config['username'],
                    ssh_config.get('password'),
                    ssh_config.get('key_file')
                )
                if not conn_ok:
                    raise Exception(f"Error de conexion SSH: {conn_msg}")

                self.download_signals.message.emit(
                    "Conexion SSH establecida", "success"
                )

                # Verify remote folder
                self.download_signals.message.emit(
                    "Verificando carpeta remota...", "info"
                )
                stdin, stdout, stderr = ssh_client.client.exec_command(
                    f'test -d "{ssh_config["remote_folder"]}" '
                    f'&& test -w "{ssh_config["remote_folder"]}" '
                    f'&& echo "OK" || echo "ERROR"'
                )
                folder_check = stdout.read().decode().strip()
                if folder_check != "OK":
                    create_ok, create_msg = ssh_client.create_directory(
                        ssh_config['remote_folder']
                    )
                    if not create_ok:
                        raise Exception(
                            f"No se puede acceder a la carpeta remota: {create_msg}"
                        )

                # ── Phase 3: SSH upload ────────────────────────────
                if self._cancel_event.is_set():
                    ssh_client.disconnect()
                    self._remove_temp(actual_file, temp_output_dir)
                    return

                remote_filename = os.path.basename(actual_file)
                remote_path = os.path.join(
                    ssh_config['remote_folder'], remote_filename
                )
                file_size_mb = file_size / 1024 / 1024

                self.download_signals.message.emit(
                    f"Subiendo {remote_filename} ({file_size_mb:.2f} MB) "
                    f"a {ssh_config['remote_folder']}...",
                    "info"
                )
                self.progress_hook.progress.emit(70, "Subiendo archivo...")

                def _upload_progress(transferred, total):
                    if total > 0:
                        pct = int(70 + (transferred / total) * 28)
                        self.download_signals.progress_update.emit(
                            pct, f"Subiendo... {transferred / 1024 / 1024:.1f} / {total / 1024 / 1024:.1f} MB"
                        )

                upload_ok, upload_msg = ssh_client.upload_file(
                    actual_file, remote_path, progress_callback=_upload_progress
                )

                ssh_client.disconnect()

                if upload_ok:
                    self.download_signals.message.emit(upload_msg, "success")
                    if ssh_config.get('remote_folder'):
                        self.app_settings.set_last_remote_folder(
                            ssh_config['remote_folder']
                        )
                    self._remove_temp(actual_file, temp_output_dir)
                    self.progress_hook.progress.emit(
                        100, "Descarga y subida completadas!"
                    )
                    self.download_signals.message.emit(
                        f"Archivo subido exitosamente a: {remote_path}!",
                        "success"
                    )
                    self.download_signals.download_finished.emit(
                        True,
                        f"Descarga y subida completadas!\n\n{title}"
                        f"\n\nGuardado en servidor: {remote_path}",
                        title
                    )
                else:
                    raise Exception(f"Error al subir archivo: {upload_msg}")

            else:
                # ── Local download ─────────────────────────────────
                success, message, title = YouTubeDownloader.download(
                    url, output_folder, is_audio, quality, self.progress_hook
                )

                if not success:
                    raise Exception(message)

                if output_folder:
                    self.app_settings.set_last_local_folder(output_folder)

                transcription_result = ""

                # ── Phase 4: transcription (local only) ────────────
                if is_audio and transcribe:
                    if self._cancel_event.is_set():
                        return

                    self.progress_hook.progress.emit(
                        95, "Transcribiendo audio..."
                    )
                    self.download_signals.message.emit(
                        "Iniciando transcripcion con Whisper AI...", "info"
                    )

                    time.sleep(1)  # Wait for file write to finish

                    mp3_files = glob.glob(
                        os.path.join(output_folder, "*.mp3")
                    )
                    if mp3_files:
                        audio_file = max(mp3_files, key=os.path.getmtime)
                        txt_filename = (
                            os.path.splitext(audio_file)[0]
                            + "_transcripcion.txt"
                        )
                        trans_ok, trans_msg, _ = AudioTranscriber.transcribe(
                            audio_file, txt_filename,
                            model_name=whisper_model, language="es"
                        )
                        if trans_ok:
                            self.download_signals.message.emit(
                                f"Transcripcion guardada: "
                                f"{os.path.basename(txt_filename)}",
                                "success"
                            )
                            transcription_result = (
                                f"\nTranscripcion: {txt_filename}"
                            )
                        else:
                            self.download_signals.message.emit(
                                f"Error en transcripcion: {trans_msg}",
                                "warning"
                            )
                            transcription_result = (
                                f"\nTranscripcion fallida: {trans_msg}"
                            )
                    else:
                        self.download_signals.message.emit(
                            "No se encontro archivo de audio para transcribir",
                            "warning"
                        )

                self.progress_hook.progress.emit(100, "Descarga completada!")
                self.download_signals.message.emit(
                    f"Descarga completada! Archivo guardado en: {output_folder}",
                    "success"
                )
                self.download_signals.download_finished.emit(
                    True,
                    f"Descarga completada!\n\n{title}"
                    f"\n\nGuardado en: {output_folder}{transcription_result}",
                    title
                )

        except DownloadCancelled:
            logger.info("Download cancelled by user")
            self.download_signals.message.emit("Descarga cancelada", "warning")
            self.download_signals.download_finished.emit(
                False, "Descarga cancelada por el usuario", ""
            )
        except Exception as e:
            error_msg = str(e)
            logger.exception("Error during download")
            self.download_signals.message.emit(
                f"Error en la descarga: {error_msg}", "error"
            )
            self.download_signals.download_finished.emit(
                False,
                f"Error al descargar el video:\n\n{error_msg}",
                ""
            )

    # ------------------------------------------------------------------
    # Post-download
    # ------------------------------------------------------------------

    def on_download_finished(self, success: bool, message: str, title: str):
        """Re-enables UI and shows result dialog"""
        self.download_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress.set_status(">> SISTEMA LISTO")

        if success:
            self.show_dialog_safe("Exito", message, "info")
        else:
            self.show_dialog_safe("Error", message, "error")

    def show_dialog_safe(self, title: str, message: str, dialog_type: str):
        """Shows a dialog safely (callable from any thread via signal)"""
        if dialog_type == "info":
            QMessageBox.information(self, title, message)
        elif dialog_type == "error":
            QMessageBox.critical(self, title, message)
        elif dialog_type == "warning":
            QMessageBox.warning(self, title, message)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_downloaded_file(temp_dir, files_before, is_audio, video_title):
        """Locate the most recently created file matching the expected extension."""
        if not os.path.exists(temp_dir):
            return None

        files_after = set(os.listdir(temp_dir))
        new_files = files_after - files_before
        expected_ext = '.mp3' if is_audio else '.mp4'

        # 1. Among new files, prefer matching extension
        if new_files:
            matching = [f for f in new_files if f.endswith(expected_ext)]
            if matching:
                return max(
                    [os.path.join(temp_dir, f) for f in matching],
                    key=os.path.getmtime
                )
            # 2. Any new file
            return max(
                [os.path.join(temp_dir, f) for f in new_files],
                key=os.path.getmtime
            )

        # 3. Fallback: newest file with matching extension anywhere
        all_matching = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, f)) and f.endswith(expected_ext)
        ]
        if all_matching:
            return max(all_matching, key=os.path.getmtime)

        # 4. Last resort: newest file of any type
        all_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if os.path.isfile(os.path.join(temp_dir, f))
        ]
        if all_files:
            return max(all_files, key=os.path.getmtime)

        return None

    @staticmethod
    def _remove_temp(file_path, temp_dir):
        """Remove a temp file and its directory if empty."""
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
        except OSError as exc:
            logger.warning("Could not remove temp file %s: %s", file_path, exc)
        try:
            if temp_dir and os.path.isdir(temp_dir) and not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except OSError:
            pass

    def _cleanup_temp_files(self):
        """Remove leftover temp files from previous sessions."""
        temp_dir = os.path.join(tempfile.gettempdir(), "youtube_download")
        if not os.path.isdir(temp_dir):
            return
        try:
            for f in os.listdir(temp_dir):
                fp = os.path.join(temp_dir, f)
                if os.path.isfile(fp):
                    try:
                        os.remove(fp)
                    except OSError:
                        pass
            if not os.listdir(temp_dir):
                os.rmdir(temp_dir)
        except OSError:
            pass
