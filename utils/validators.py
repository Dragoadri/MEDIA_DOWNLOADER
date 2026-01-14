#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidades de validación
"""

from pathlib import Path
from config import SUPPORTED_PLATFORMS


class InputValidator:
    """Clase para validar entradas del usuario"""

    @staticmethod
    def validate_url(url, platform=None):
        """
        Valida que la URL sea válida para la plataforma seleccionada

        Args:
            url: URL a validar
            platform: Plataforma seleccionada (opcional)

        Returns:
            tuple: (válido: bool, mensaje: str)
        """
        if not url or not url.strip():
            return False, "La URL no puede estar vacía"

        url = url.strip()

        # Verificar que tenga formato de URL
        if not url.startswith(('http://', 'https://')):
            return False, "La URL debe comenzar con http:// o https://"

        # Si se especifica "Otra URL", aceptar cualquier URL válida
        if platform == "Otra URL":
            return True, ""

        # Si se especifica una plataforma, validar contra sus dominios
        if platform and platform in SUPPORTED_PLATFORMS:
            domains = SUPPORTED_PLATFORMS[platform]["domains"]
            if domains and not any(domain in url for domain in domains):
                return False, f"La URL no parece ser de {platform}"

        return True, ""

    @staticmethod
    def detect_platform(url):
        """
        Detecta automáticamente la plataforma de una URL

        Args:
            url: URL a analizar

        Returns:
            str: Nombre de la plataforma o "Otra URL" si no se reconoce
        """
        if not url:
            return None

        url = url.strip().lower()

        for platform_name, platform_info in SUPPORTED_PLATFORMS.items():
            if platform_name == "Otra URL":
                continue
            domains = platform_info.get("domains", [])
            if any(domain in url for domain in domains):
                return platform_name

        return "Otra URL"

    @staticmethod
    def get_platform_capabilities(platform):
        """
        Obtiene las capacidades de una plataforma

        Args:
            platform: Nombre de la plataforma

        Returns:
            dict: Capacidades (supports_video, supports_audio)
        """
        if platform in SUPPORTED_PLATFORMS:
            return {
                "supports_video": SUPPORTED_PLATFORMS[platform]["supports_video"],
                "supports_audio": SUPPORTED_PLATFORMS[platform]["supports_audio"]
            }
        return {"supports_video": True, "supports_audio": True}
    
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
