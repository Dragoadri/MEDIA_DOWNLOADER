#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestor de configuraciones SSH guardadas
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional


class SSHConfigManager:
    """Gestor para guardar y cargar configuraciones SSH"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Inicializa el gestor de configuraciones
        
        Args:
            config_file: Ruta al archivo de configuración. Si es None, usa el predeterminado.
        """
        if config_file is None:
            config_dir = Path.home() / ".youtube_downloader"
            config_dir.mkdir(exist_ok=True)
            self.config_file = config_dir / "ssh_config.json"
        else:
            self.config_file = Path(config_file)
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_configs(self) -> List[Dict]:
        """
        Carga las configuraciones SSH guardadas
        
        Returns:
            Lista de configuraciones SSH
        """
        if not self.config_file.exists():
            return []
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('servers', [])
        except Exception:
            return []
    
    def save_config(self, name: str, host: str, port: int, username: str,
                   password: str = "", key_file: str = "", 
                   remote_folder: str = "", description: str = "") -> bool:
        """
        Guarda una nueva configuración SSH
        
        Args:
            name: Nombre de la configuración
            host: Host del servidor
            port: Puerto SSH
            username: Usuario
            password: Contraseña (se guarda, pero se recomienda usar claves)
            key_file: Ruta a la clave privada
            remote_folder: Carpeta remota por defecto
            description: Descripción opcional
            
        Returns:
            True si se guardó correctamente
        """
        try:
            configs = self.load_configs()
            
            # Verificar si ya existe una configuración con el mismo nombre
            configs = [c for c in configs if c.get('name') != name]
            
            # Añadir nueva configuración
            new_config = {
                'name': name,
                'host': host,
                'port': port,
                'username': username,
                'password': password,  # ⚠️ Se guarda en texto plano
                'key_file': key_file,
                'remote_folder': remote_folder,
                'description': description
            }
            
            configs.append(new_config)
            
            # Guardar
            data = {'servers': configs}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def delete_config(self, name: str) -> bool:
        """
        Elimina una configuración SSH
        
        Args:
            name: Nombre de la configuración a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            configs = self.load_configs()
            configs = [c for c in configs if c.get('name') != name]
            
            data = {'servers': configs}
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception:
            return False
    
    def get_config(self, name: str) -> Optional[Dict]:
        """
        Obtiene una configuración específica por nombre
        
        Args:
            name: Nombre de la configuración
            
        Returns:
            Diccionario con la configuración o None si no existe
        """
        configs = self.load_configs()
        for config in configs:
            if config.get('name') == name:
                return config
        return None
