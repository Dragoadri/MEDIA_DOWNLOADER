#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Widget de opciones de descarga: formato, calidad, transcripcion y modelo Whisper.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QGroupBox, QRadioButton, QCheckBox
)
from PySide6.QtCore import Signal

from config import VIDEO_QUALITIES, SUPPORTED_PLATFORMS, MATRIX_COLORS
from download.transcriber import AudioTranscriber


class OptionsWidget(QWidget):
    """Widget para configurar formato, calidad y transcripcion"""

    format_changed = Signal(bool)  # True = audio

    def __init__(self, default_format: str = "audio", parent=None):
        """
        Inicializa el widget de opciones.

        Args:
            default_format: Formato por defecto ('audio' o 'video')
            parent: Widget padre
        """
        super().__init__(parent)
        self._default_format = default_format
        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz del widget"""
        group = QGroupBox(">> OPCIONES")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(10)

        # Formato
        format_layout = QHBoxLayout()
        format_label = QLabel("Formato:")
        format_label.setMinimumWidth(90)
        self.format_video = QRadioButton("Video (MP4)")
        self.format_audio = QRadioButton("Audio (MP3)")

        # Formato por defecto
        if self._default_format == 'audio':
            self.format_audio.setChecked(True)
        else:
            self.format_video.setChecked(True)

        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_video)
        format_layout.addWidget(self.format_audio)
        format_layout.addStretch()
        group_layout.addLayout(format_layout)

        # Calidad (solo para video)
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Calidad:")
        quality_label.setMinimumWidth(90)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(VIDEO_QUALITIES)
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo, 1)
        quality_layout.addStretch(2)
        group_layout.addLayout(quality_layout)

        # Opcion de transcripcion (solo para audio)
        transcription_layout = QHBoxLayout()
        transcription_label = QLabel("Extra:")
        transcription_label.setMinimumWidth(90)
        self.transcription_checkbox = QCheckBox("Generar transcripcion (TXT)")
        self.transcription_checkbox.setToolTip(
            "Genera un archivo de texto con la transcripcion del audio usando IA"
        )
        self.transcription_checkbox.setEnabled(self.format_audio.isChecked())
        self.transcription_checkbox.toggled.connect(self._on_transcription_toggled)
        transcription_layout.addWidget(transcription_label)
        transcription_layout.addWidget(self.transcription_checkbox)
        transcription_layout.addStretch()
        group_layout.addLayout(transcription_layout)

        # Selector de modelo Whisper
        whisper_layout = QHBoxLayout()
        whisper_label = QLabel("Modelo:")
        whisper_label.setMinimumWidth(90)
        self.whisper_model_combo = QComboBox()

        # Poblar con modelos disponibles
        model_info = AudioTranscriber.get_model_info()
        for model_name, info in model_info.items():
            display_text = f"{model_name} ({info['size']} - {info['quality']})"
            self.whisper_model_combo.addItem(display_text, model_name)

        # Modelo por defecto: "base" (indice 1)
        self.whisper_model_combo.setCurrentIndex(1)
        self.whisper_model_combo.setEnabled(False)
        self.whisper_model_combo.setToolTip("Selecciona el modelo de Whisper para la transcripcion")

        whisper_layout.addWidget(whisper_label)
        whisper_layout.addWidget(self.whisper_model_combo, 1)
        whisper_layout.addStretch(2)
        group_layout.addLayout(whisper_layout)

        # Mensaje de capacidades de plataforma
        self.platform_capabilities_label = QLabel("")
        self.platform_capabilities_label.setStyleSheet(
            f"color: {MATRIX_COLORS['warning']}; font-size: 9pt; padding-left: 95px;"
        )
        group_layout.addWidget(self.platform_capabilities_label)

        # Mensaje de transcripcion
        self.transcription_info_label = QLabel("")
        self.transcription_info_label.setStyleSheet(
            f"color: {MATRIX_COLORS['info']}; font-size: 9pt; padding-left: 95px;"
        )
        group_layout.addWidget(self.transcription_info_label)

        group.setLayout(group_layout)

        # Layout principal del widget
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(group)
        self.setLayout(layout)

        # Conectar cambio de formato
        self.format_video.toggled.connect(self._on_format_changed)
        self.format_audio.toggled.connect(self._on_format_changed)

    def _on_format_changed(self):
        """Habilita o deshabilita opciones segun el formato seleccionado"""
        is_video = self.format_video.isChecked()
        is_audio = self.format_audio.isChecked()

        self.quality_combo.setEnabled(is_video)
        self.transcription_checkbox.setEnabled(is_audio)

        if is_video:
            self.transcription_checkbox.setChecked(False)
            self.transcription_info_label.setText("")
            self.whisper_model_combo.setEnabled(False)
        else:
            self.transcription_info_label.setText(
                "La transcripcion usa Whisper AI (puede tardar)"
            )
            # Solo habilitar whisper si transcripcion esta marcada
            self.whisper_model_combo.setEnabled(self.transcription_checkbox.isChecked())

        self.format_changed.emit(is_audio)

    def _on_transcription_toggled(self, checked):
        """Habilita/deshabilita selector de modelo Whisper segun transcripcion"""
        is_audio = self.format_audio.isChecked()
        self.whisper_model_combo.setEnabled(checked and is_audio)

    def is_audio(self) -> bool:
        """Retorna True si el formato seleccionado es audio"""
        return self.format_audio.isChecked()

    def get_quality(self) -> str:
        """Retorna la calidad de video seleccionada"""
        return self.quality_combo.currentText()

    def should_transcribe(self) -> bool:
        """Retorna True si la transcripcion esta habilitada"""
        return self.transcription_checkbox.isChecked() and self.format_audio.isChecked()

    def get_whisper_model(self) -> str:
        """Retorna el nombre del modelo Whisper seleccionado"""
        return self.whisper_model_combo.currentData()

    def update_platform_capabilities(self, platform: str):
        """
        Actualiza las opciones de formato segun las capacidades de la plataforma.

        Args:
            platform: Nombre de la plataforma
        """
        if platform and platform in SUPPORTED_PLATFORMS:
            capabilities = SUPPORTED_PLATFORMS[platform]

            if not capabilities["supports_video"]:
                self.format_audio.setChecked(True)
                self.format_video.setEnabled(False)
                self.quality_combo.setEnabled(False)
                self.platform_capabilities_label.setText(
                    "Esta plataforma solo soporta audio"
                )
            elif not capabilities["supports_audio"]:
                self.format_video.setChecked(True)
                self.format_audio.setEnabled(False)
                self.quality_combo.setEnabled(True)
                self.platform_capabilities_label.setText(
                    "Esta plataforma solo soporta video"
                )
            else:
                self.format_video.setEnabled(True)
                self.format_audio.setEnabled(True)
                self.quality_combo.setEnabled(self.format_video.isChecked())
                self.platform_capabilities_label.setText("")
