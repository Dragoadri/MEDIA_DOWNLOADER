#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades de validación
"""

from pathlib import Path


class InputValidator:
    """Clase para validar entradas del usuario"""
    
    @staticmethod
    def validate_url(url):
        """
        Valida que la URL sea válida
        
        Args:
            url: URL a validar
            
        Returns:
            tuple: (válido: bool, mensaje: str)
        """
        if not url or not url.strip():
            return False, "La URL no puede estar vacía"
        
        url = url.strip()
        
        # Verificar que sea una URL de YouTube
        youtube_domains = [
            'youtube.com',
            'www.youtube.com',
            'youtu.be',
            'm.youtube.com'
        ]
        
        if not any(domain in url for domain in youtube_domains):
            return False, "Por favor, introduce una URL válida de YouTube"
        
        return True, ""
    
    @staticmethod
    def validate_folder(folder_path):
        """
        Valida que la carpeta exista o pueda crearse
        
        Args:
            folder_path: Ruta de la carpeta
            
        Returns:
            tuple: (válido: bool, mensaje: str)
        """
        if not folder_path or not folder_path.strip():
            return False, "La carpeta de destino no puede estar vacía"
        
        folder_path = Path(folder_path.strip())
        
        # Intentar crear la carpeta si no existe
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"No se puede crear la carpeta: {str(e)}"
        
        # Verificar que sea un directorio
        if not folder_path.is_dir():
            return False, "La ruta especificada no es una carpeta válida"
        
        return True, ""
    
    @staticmethod
    def validate_all(url, folder_path):
        """
        Valida URL y carpeta
        
        Args:
            url: URL a validar
            folder_path: Ruta de la carpeta
            
        Returns:
            tuple: (válido: bool, mensaje: str)
        """
        # Validar URL
        url_valid, url_msg = InputValidator.validate_url(url)
        if not url_valid:
            return False, url_msg
        
        # Validar carpeta
        folder_valid, folder_msg = InputValidator.validate_folder(folder_path)
        if not folder_valid:
            return False, folder_msg
        
        return True, ""
