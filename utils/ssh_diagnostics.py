#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herramientas de diagnóstico SSH
"""

import logging

from utils.ssh_client import SSHClient

logger = logging.getLogger(__name__)


def test_ssh_upload(host, port, username, password, key_file, remote_folder, test_file_path=None):
    """
    Prueba la subida de archivo SSH con diagnóstico completo
    
    Args:
        host: Host del servidor
        port: Puerto SSH
        username: Usuario
        password: Contraseña
        key_file: Ruta a clave privada
        remote_folder: Carpeta remota
        test_file_path: Ruta a archivo de prueba (opcional)
    """
    logger.info("SSH diagnostics started")
    logger.info("=" * 50)

    # Conectar
    logger.info("1. Conectando a %s@%s:%s...", username, host, port)
    ssh_client = SSHClient()
    success, message = ssh_client.connect(host, port, username, password, key_file)

    if not success:
        logger.warning("Error de conexión: %s", message)
        return False

    logger.info("Conexión establecida")

    # Probar comando básico
    logger.info("2. Probando comando básico...")
    test_success, test_msg = ssh_client.test_connection()
    if test_success:
        logger.info("Comando básico funciona")
    else:
        logger.warning("%s", test_msg)

    # Verificar carpeta remota
    logger.info("3. Verificando carpeta remota: %s", remote_folder)
    stdin, stdout, stderr = ssh_client.client.exec_command(f'test -d "{remote_folder}" && echo "EXISTS" || echo "NOT_EXISTS"')
    folder_exists = stdout.read().decode().strip()

    if folder_exists == "EXISTS":
        logger.info("La carpeta existe")

        # Verificar permisos de escritura
        stdin, stdout, stderr = ssh_client.client.exec_command(f'test -w "{remote_folder}" && echo "WRITABLE" || echo "NOT_WRITABLE"')
        is_writable = stdout.read().decode().strip()

        if is_writable == "WRITABLE":
            logger.info("La carpeta tiene permisos de escritura")
        else:
            logger.warning("La carpeta NO tiene permisos de escritura")
            logger.info("   Solución: chmod 755 en el servidor")
    else:
        logger.warning("La carpeta NO existe")
        logger.info("   Intentando crear: %s", remote_folder)
        create_success, create_msg = ssh_client.create_directory(remote_folder)
        if create_success:
            logger.info("Carpeta creada")
        else:
            logger.warning("No se pudo crear: %s", create_msg)

    # Verificar espacio en disco
    logger.info("4. Verificando espacio en disco...")
    stdin, stdout, stderr = ssh_client.client.exec_command(f'df -h "{remote_folder}"')
    disk_info = stdout.read().decode()
    logger.info(disk_info)

    # Probar subida de archivo pequeño si se proporciona
    if test_file_path:
        logger.info("5. Probando subida de archivo de prueba...")
        import os
        if os.path.exists(test_file_path):
            remote_test_path = f"{remote_folder}/test_upload.tmp"
            upload_success, upload_msg = ssh_client.upload_file(test_file_path, remote_test_path)
            if upload_success:
                logger.info("Subida de prueba exitosa")
                # Eliminar archivo de prueba
                try:
                    ssh_client.sftp.remove(remote_test_path)
                except (IOError, OSError):
                    pass
            else:
                logger.warning("Error en subida de prueba: %s", upload_msg)
        else:
            logger.warning("Archivo de prueba no encontrado: %s", test_file_path)

    ssh_client.disconnect()
    logger.info("=" * 50)
    logger.info("Diagnóstico completado")

    return True
