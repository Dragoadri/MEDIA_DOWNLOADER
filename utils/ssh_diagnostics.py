#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herramientas de diagnóstico SSH
"""

from utils.ssh_client import SSHClient


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
    print("🔍 Diagnóstico SSH")
    print("=" * 50)
    
    # Conectar
    print(f"\n1. Conectando a {username}@{host}:{port}...")
    ssh_client = SSHClient()
    success, message = ssh_client.connect(host, port, username, password, key_file)
    
    if not success:
        print(f"❌ Error de conexión: {message}")
        return False
    
    print("✅ Conexión establecida")
    
    # Probar comando básico
    print(f"\n2. Probando comando básico...")
    test_success, test_msg = ssh_client.test_connection()
    if test_success:
        print("✅ Comando básico funciona")
    else:
        print(f"⚠️ {test_msg}")
    
    # Verificar carpeta remota
    print(f"\n3. Verificando carpeta remota: {remote_folder}")
    stdin, stdout, stderr = ssh_client.client.exec_command(f'test -d "{remote_folder}" && echo "EXISTS" || echo "NOT_EXISTS"')
    folder_exists = stdout.read().decode().strip()
    
    if folder_exists == "EXISTS":
        print("✅ La carpeta existe")
        
        # Verificar permisos de escritura
        stdin, stdout, stderr = ssh_client.client.exec_command(f'test -w "{remote_folder}" && echo "WRITABLE" || echo "NOT_WRITABLE"')
        is_writable = stdout.read().decode().strip()
        
        if is_writable == "WRITABLE":
            print("✅ La carpeta tiene permisos de escritura")
        else:
            print("❌ La carpeta NO tiene permisos de escritura")
            print("   Solución: chmod 755 en el servidor")
    else:
        print("❌ La carpeta NO existe")
        print(f"   Intentando crear: {remote_folder}")
        create_success, create_msg = ssh_client.create_directory(remote_folder)
        if create_success:
            print("✅ Carpeta creada")
        else:
            print(f"❌ No se pudo crear: {create_msg}")
    
    # Verificar espacio en disco
    print(f"\n4. Verificando espacio en disco...")
    stdin, stdout, stderr = ssh_client.client.exec_command(f'df -h "{remote_folder}"')
    disk_info = stdout.read().decode()
    print(disk_info)
    
    # Probar subida de archivo pequeño si se proporciona
    if test_file_path:
        print(f"\n5. Probando subida de archivo de prueba...")
        import os
        if os.path.exists(test_file_path):
            remote_test_path = f"{remote_folder}/test_upload.tmp"
            upload_success, upload_msg = ssh_client.upload_file(test_file_path, remote_test_path)
            if upload_success:
                print("✅ Subida de prueba exitosa")
                # Eliminar archivo de prueba
                try:
                    ssh_client.sftp.remove(remote_test_path)
                except:
                    pass
            else:
                print(f"❌ Error en subida de prueba: {upload_msg}")
        else:
            print(f"⚠️ Archivo de prueba no encontrado: {test_file_path}")
    
    ssh_client.disconnect()
    print("\n" + "=" * 50)
    print("✅ Diagnóstico completado")
    
    return True
