#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hook para capturar el progreso de la descarga
"""

from PySide6.QtCore import QObject, Signal


class DownloadProgressHook(QObject):
    """Hook para capturar el progreso de la descarga"""
    progress = Signal(int, str)  # porcentaje, mensaje
    
    def __init__(self):
        super().__init__()
        self._last_percent = 0
    
    def hook(self, d):
        """
        Hook que se llama durante la descarga para reportar el progreso
        
        Args:
            d: Diccionario con información del estado de la descarga
        """
        if d['status'] == 'downloading':
            # Calcular porcentaje
            if 'total_bytes' in d:
                percent = int((d['downloaded_bytes'] / d['total_bytes']) * 100)
            elif 'total_bytes_estimate' in d:
                percent = int((d['downloaded_bytes'] / d['total_bytes_estimate']) * 100)
            else:
                percent = self._last_percent
            
            self._last_percent = percent
            
            # Calcular velocidad
            speed = d.get('speed', 0)
            if speed:
                speed_str = f"{speed / 1024 / 1024:.2f} MB/s"
            else:
                speed_str = "Calculando..."
            
            message = f"Descargando... {speed_str}"
            self.progress.emit(percent, message)
        
        elif d['status'] == 'finished':
            self.progress.emit(100, "Procesando archivo...")
        
        elif d['status'] == 'error':
            error_msg = d.get('error', 'Error desconocido')
            self.progress.emit(0, f"Error: {error_msg}")
