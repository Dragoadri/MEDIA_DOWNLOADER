# 🔍 Verificación del Servidor SSH

Si la subida de archivos se queda bloqueada, verifica lo siguiente en tu servidor:

## ✅ Verificaciones en el Servidor

### 1. Verificar que el servicio SSH está activo

```bash
# En el servidor
sudo systemctl status ssh
# o
sudo systemctl status sshd
```

### 2. Verificar permisos de la carpeta de destino

```bash
# En el servidor (reemplaza con tu ruta)
ls -ld /home/usuario/Descargas
# Debe mostrar permisos de escritura (drwxr-xr-x o similar)

# Si no tiene permisos, corregir:
chmod 755 /home/usuario/Descargas
```

### 3. Verificar espacio en disco

```bash
# En el servidor (reemplaza con tu ruta)
df -h /home/usuario/Descargas
```

### 4. Verificar que el usuario tiene permisos

```bash
# En el servidor, como tu usuario
touch /home/usuario/Descargas/test.txt
# Si funciona, eliminar:
rm /home/usuario/Descargas/test.txt
```

### 5. Verificar configuración SSH

```bash
# En el servidor
sudo nano /etc/ssh/sshd_config

# Verificar que estas líneas NO estén comentadas:
# Subsystem sftp /usr/lib/openssh/sftp-server
# PermitRootLogin no (o yes si necesitas root)
```

### 6. Reiniciar servicio SSH si es necesario

```bash
# En el servidor
sudo systemctl restart ssh
# o
sudo systemctl restart sshd
```

## 🧪 Prueba Manual de Subida

Desde tu ordenador local, prueba subir un archivo manualmente:

```bash
# Probar con scp (reemplaza con tus datos)
scp /ruta/a/archivo.mp3 usuario@servidor:/home/usuario/Descargas/

# O con contraseña usando sshpass (no recomendado para producción)
sshpass -p 'tu_contraseña' scp /ruta/a/archivo.mp3 usuario@servidor:/home/usuario/Descargas/

# O usando clave SSH (recomendado)
scp -i /ruta/a/clave_privada /ruta/a/archivo.mp3 usuario@servidor:/home/usuario/Descargas/
```

Si esto funciona, el problema está en el código. Si no funciona, el problema está en el servidor.

## 🔧 Soluciones Comunes

### Problema: "Permission denied"
**Solución:**
```bash
# En el servidor (reemplaza con tu usuario y ruta)
chmod 755 /home/usuario/Descargas
chown usuario:usuario /home/usuario/Descargas
```

### Problema: "No space left on device"
**Solución:**
```bash
# En el servidor, liberar espacio
df -h
du -sh /home/drago/Descargas/*
```

### Problema: "Connection timeout"
**Solución:**
- Verificar que el servidor esté encendido
- Verificar firewall: `sudo ufw status`
- Verificar que el puerto 22 esté abierto

## 📝 Logs del Servidor

Para ver qué está pasando en el servidor:

```bash
# En el servidor
sudo tail -f /var/log/auth.log
# Intenta subir un archivo y observa los logs
```
