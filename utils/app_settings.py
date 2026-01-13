#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de configuraciones de la aplicación
"""

import json
from pathlib import Path
from typing import Optional


class AppSettings:
    """Gestor para guardar y cargar configuraciones de la aplicación"""
    
    def __init__(self, settings_file: Optional[str] = None):
        """
        Inicializa el gestor de configuraciones
        
        Args:
            settings_file: Ruta al archivo de configuración. Si es None, usa el predeterminado.
        """
        if settings_file is None:
            config_dir = Path.home() / ".youtube_downloader"
            config_dir.mkdir(exist_ok=True)
            self.settings_file = config_dir / "app_settings.json"
        else:
            self.settings_file = Path(settings_file)
        
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_settings(self) -> dict:
        """
        Carga las configuraciones guardadas
        
        Returns:
            Diccionario con las configuraciones
        """
        if not self.settings_file.exists():
            return {}
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def save_settings(self, settings: dict) -> bool:
        """
        Guarda las configuraciones
        
        Args:
            settings: Diccionario con las configuraciones
            
        Returns:
            True si se guardó correctamente
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def get_last_local_folder(self) -> Optional[str]:
        """Obtiene la última carpeta local usada"""
        settings = self.load_settings()
        return settings.get('last_local_folder')
    
    def set_last_local_folder(self, folder: str) -> bool:
        """Guarda la última carpeta local usada"""
        settings = self.load_settings()
        settings['last_local_folder'] = folder
        return self.save_settings(settings)
    
    def get_last_remote_folder(self) -> Optional[str]:
        """Obtiene la última carpeta remota usada"""
        settings = self.load_settings()
        return settings.get('last_remote_folder')
    
    def set_last_remote_folder(self, folder: str) -> bool:
        """Guarda la última carpeta remota usada"""
        settings = self.load_settings()
        settings['last_remote_folder'] = folder
        return self.save_settings(settings)
    
    def get_default_format(self) -> str:
        """Obtiene el formato por defecto (audio o video)"""
        settings = self.load_settings()
        return settings.get('default_format', 'audio')  # Por defecto audio
    
    def set_default_format(self, format_type: str) -> bool:
        """Guarda el formato por defecto"""
        settings = self.load_settings()
        settings['default_format'] = format_type
        return self.save_settings(settings)
