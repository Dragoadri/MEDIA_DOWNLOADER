#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente SSH para transferencia de archivos a servidor remoto
"""

import logging
import os
import paramiko
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class SSHClient:
    """Cliente SSH para conexión y transferencia de archivos"""
    
    def __init__(self):
        self.client = None
        self.sftp = None
        self.ssh_config = None
    
    def connect(self, host: str, port: int, username: str, 
                password: Optional[str] = None, 
                key_file: Optional[str] = None) -> Tuple[bool, str]:
        """
        Conecta al servidor SSH
        
        Args:
            host: Dirección del servidor
            port: Puerto SSH (normalmente 22)
            username: Nombre de usuario
            password: Contraseña (opcional si se usa clave)
            key_file: Ruta al archivo de clave privada (opcional)
            
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        try:
            # Guardar configuración para uso posterior
            self.ssh_config = {
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'key_file': key_file
            }
            
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.WarningPolicy())
            # Load known hosts if available
            known_hosts = Path.home() / ".ssh" / "known_hosts"
            if known_hosts.exists():
                self.client.load_host_keys(str(known_hosts))
            
            # Intentar con clave privada primero
            if key_file and os.path.exists(key_file):
                try:
                    self.client.connect(
                        hostname=host,
                        port=port,
                        username=username,
                        key_filename=key_file,
                        timeout=10
                    )
                except Exception as e:
                    # Si falla con clave, intentar con contraseña
                    if password:
                        self.client.connect(
                            hostname=host,
                            port=port,
                            username=username,
                            password=password,
                            timeout=10
                        )
                    else:
                        raise e
            elif password:
                # Conectar con contraseña
                self.client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=10
                )
            else:
                # Intentar con clave por defecto
                self.client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    timeout=10
                )
            
            # Crear cliente SFTP
            self.sftp = self.client.open_sftp()
            
            return True, "Conexión exitosa"
        
        except paramiko.AuthenticationException:
            return False, "Error de autenticación. Verifica usuario/contraseña o clave."
        except paramiko.SSHException as e:
            return False, f"Error SSH: {str(e)}"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"
    
    def disconnect(self):
        """Cierra la conexión SSH"""
        try:
            if self.sftp:
                self.sftp.close()
            if self.client:
                self.client.close()
        except (paramiko.SSHException, OSError) as e:
            logger.warning("Error closing SSH connection: %s", e)
        finally:
            self.sftp = None
            self.client = None

    def test_connection(self) -> Tuple[bool, str]:
        """
        Prueba la conexión SSH
        
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if not self.client:
            return False, "No hay conexión establecida"
        
        try:
            stdin, stdout, stderr = self.client.exec_command('echo "test"')
            stdout.channel.recv_exit_status()
            return True, "Conexión activa"
        except Exception as e:
            return False, f"Error al probar conexión: {str(e)}"
    
    def list_directory(self, remote_path: str) -> Tuple[bool, list, str]:
        """
        Lista el contenido de un directorio remoto
        
        Args:
            remote_path: Ruta del directorio remoto
            
        Returns:
            tuple: (éxito: bool, lista: list, mensaje: str)
        """
        if not self.sftp:
            return False, [], "No hay conexión SFTP establecida"
        
        try:
            items = self.sftp.listdir(remote_path)
            return True, items, "Directorio listado correctamente"
        except FileNotFoundError:
            return False, [], f"El directorio '{remote_path}' no existe"
        except Exception as e:
            return False, [], f"Error al listar directorio: {str(e)}"
    
    def create_directory(self, remote_path: str) -> Tuple[bool, str]:
        """
        Crea un directorio en el servidor remoto
        
        Args:
            remote_path: Ruta del directorio a crear
            
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if not self.client:
            return False, "No hay conexión establecida"
        
        try:
            # Crear directorio recursivamente
            stdin, stdout, stderr = self.client.exec_command(f'mkdir -p "{remote_path}"')
            exit_status = stdout.channel.recv_exit_status()
            
            if exit_status == 0:
                return True, "Directorio creado correctamente"
            else:
                error = stderr.read().decode()
                return False, f"Error al crear directorio: {error}"
        except Exception as e:
            return False, f"Error al crear directorio: {str(e)}"
    
    def upload_file(self, local_path: str, remote_path: str, 
                   progress_callback=None) -> Tuple[bool, str]:
        """
        Sube un archivo al servidor remoto usando SFTP optimizado
        
        Args:
            local_path: Ruta local del archivo
            remote_path: Ruta remota donde guardar
            progress_callback: Función callback para progreso (bytes_transferred, total_bytes)
            
        Returns:
            tuple: (éxito: bool, mensaje: str)
        """
        if not self.sftp:
            return False, "No hay conexión SFTP establecida"
        
        try:
            # Verificar que el archivo local existe
            if not os.path.exists(local_path):
                return False, f"El archivo local no existe: {local_path}"
            
            file_size = os.path.getsize(local_path)
            
            # Crear directorio remoto si no existe
            remote_dir = os.path.dirname(remote_path)
            if remote_dir:
                self.create_directory(remote_dir)
            
            # Usar SFTP con transferencia optimizada
            try:
                # Configurar timeout más largo para archivos grandes
                channel = self.sftp.get_channel()
                if channel:
                    channel.settimeout(600)  # 10 minutos
                    # Aumentar tamaño de buffer para mejor rendimiento
                    channel.set_combine_stderr(True)
                
                # Subir archivo directamente
                # Paramiko SFTP es confiable para archivos grandes
                self.sftp.put(local_path, remote_path, callback=progress_callback)
                
                # Verificar que el archivo se subió correctamente
                try:
                    remote_stat = self.sftp.stat(remote_path)
                    if remote_stat.st_size == file_size:
                        return True, f"Archivo subido correctamente ({file_size / 1024 / 1024:.2f} MB)"
                    else:
                        return False, f"Error: El archivo remoto tiene un tamaño diferente ({remote_stat.st_size} vs {file_size} bytes)"
                except (IOError, OSError):
                    # Si no se puede verificar, asumir que se subió correctamente
                    return True, "Archivo subido correctamente"
            
            except Exception as sftp_error:
                logger.error("SFTP upload failed: %s", sftp_error)
                return False, f"Error SFTP: {str(sftp_error)}"
        
        except Exception as e:
            return False, f"Error al subir archivo: {str(e)}"
    
    def file_exists(self, remote_path: str) -> bool:
        """
        Verifica si un archivo existe en el servidor remoto
        
        Args:
            remote_path: Ruta del archivo remoto
            
        Returns:
            bool: True si existe
        """
        if not self.sftp:
            return False
        
        try:
            self.sftp.stat(remote_path)
            return True
        except (IOError, OSError):
            return False
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """
        Obtiene el tamaño de un archivo remoto
        
        Args:
            remote_path: Ruta del archivo remoto
            
        Returns:
            int: Tamaño del archivo en bytes, None si no existe
        """
        if not self.sftp:
            return None
        
        try:
            stat = self.sftp.stat(remote_path)
            return stat.st_size
        except (IOError, OSError):
            return None
