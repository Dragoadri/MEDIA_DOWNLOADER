#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de la aplicación
"""

from pathlib import Path

# Configuración de la aplicación
APP_NAME = "Descargador de YouTube"
APP_VERSION = "1.0.0"

# Carpetas por defecto
DEFAULT_DOWNLOAD_FOLDER = str(Path.home() / "Descargas")

# Opciones de calidad de vídeo
VIDEO_QUALITIES = [
    "Mejor calidad disponible",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p"
]

# Configuración de audio
AUDIO_QUALITY = "192"  # kbps
AUDIO_CODEC = "mp3"

# Configuración de la ventana
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_X = 100
WINDOW_Y = 100
