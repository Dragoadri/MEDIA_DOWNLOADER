#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de la aplicación
"""

from pathlib import Path

# Configuración de la aplicación
APP_NAME = "Media Downloader"
APP_VERSION = "2.0.0"

# Carpetas por defecto
DEFAULT_DOWNLOAD_FOLDER = str(Path.home() / "Descargas")

# Plataformas soportadas
SUPPORTED_PLATFORMS = {
    "YouTube": {
        "icon": "▶",
        "domains": ["youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"],
        "supports_video": True,
        "supports_audio": True,
        "color": "#00FF41"
    },
    "Instagram": {
        "icon": "📷",
        "domains": ["instagram.com", "www.instagram.com"],
        "supports_video": True,
        "supports_audio": False,
        "color": "#E4405F"
    },
    "X (Twitter)": {
        "icon": "𝕏",
        "domains": ["twitter.com", "www.twitter.com", "x.com", "www.x.com"],
        "supports_video": True,
        "supports_audio": False,
        "color": "#1DA1F2"
    },
    "TikTok": {
        "icon": "♪",
        "domains": ["tiktok.com", "www.tiktok.com", "vm.tiktok.com"],
        "supports_video": True,
        "supports_audio": True,
        "color": "#FF0050"
    },
    "Spotify": {
        "icon": "🎵",
        "domains": ["open.spotify.com", "spotify.com"],
        "supports_video": False,
        "supports_audio": True,
        "color": "#1DB954"
    },
    "iVoox": {
        "icon": "🎙",
        "domains": ["ivoox.com", "www.ivoox.com"],
        "supports_video": False,
        "supports_audio": True,
        "color": "#FF6600"
    },
    "SoundCloud": {
        "icon": "☁",
        "domains": ["soundcloud.com", "www.soundcloud.com"],
        "supports_video": False,
        "supports_audio": True,
        "color": "#FF5500"
    },
    "Vimeo": {
        "icon": "🎬",
        "domains": ["vimeo.com", "www.vimeo.com"],
        "supports_video": True,
        "supports_audio": True,
        "color": "#1AB7EA"
    },
    "Twitch": {
        "icon": "🎮",
        "domains": ["twitch.tv", "www.twitch.tv", "clips.twitch.tv"],
        "supports_video": True,
        "supports_audio": True,
        "color": "#9146FF"
    },
    "Facebook": {
        "icon": "📘",
        "domains": ["facebook.com", "www.facebook.com", "fb.watch"],
        "supports_video": True,
        "supports_audio": False,
        "color": "#1877F2"
    },
    "Dailymotion": {
        "icon": "📺",
        "domains": ["dailymotion.com", "www.dailymotion.com"],
        "supports_video": True,
        "supports_audio": True,
        "color": "#00AAFF"
    },
    "Otra URL": {
        "icon": "🌐",
        "domains": [],
        "supports_video": True,
        "supports_audio": True,
        "color": "#00FF41"
    }
}

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
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
WINDOW_X = 100
WINDOW_Y = 100

# Tema Matrix
MATRIX_COLORS = {
    "background": "#0D0D0D",
    "background_secondary": "#1A1A1A",
    "background_tertiary": "#252525",
    "text": "#00FF41",
    "text_dim": "#00CC33",
    "text_bright": "#33FF66",
    "accent": "#00FF41",
    "accent_hover": "#33FF66",
    "accent_dark": "#009922",
    "border": "#00FF41",
    "border_dim": "#004D13",
    "error": "#FF0040",
    "warning": "#FFAA00",
    "success": "#00FF41",
    "info": "#00CCFF"
}
