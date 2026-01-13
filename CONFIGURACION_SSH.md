# 🔐 Configuración SSH - Guía de Uso

## Configuración Rápida del Servidor

### Configurar tu Servidor SSH

Para usar la funcionalidad de descarga a servidor remoto, necesitas configurar tu servidor SSH:

1. **Abre la aplicación** y ve a la pestaña "🌐 Servidor SSH"

2. **Completa la configuración SSH**:
   - **Host**: IP o dominio de tu servidor (ej: `192.168.1.49` o `servidor.midominio.com`)
   - **Puerto**: Puerto SSH (por defecto `22`)
   - **Usuario**: Tu usuario SSH
   - **Contraseña**: Tu contraseña SSH (opcional si usas clave SSH)
   - **Clave SSH**: Ruta a tu archivo de clave privada (opcional, recomendado)

3. **Guarda la configuración** (recomendado):
   - Introduce un nombre descriptivo (ej: "Servidor Casa", "Mi Servidor")
   - Haz clic en **"💾 Guardar"**
   - La próxima vez podrás seleccionarla del menú desplegable

4. **Prueba la conexión**:
   - Haz clic en **"🔌 Probar Conexión"** para verificar que todo funciona

5. **Especifica la carpeta remota**:
   - Ejemplo: `/home/usuario/Descargas`
   - Esta es la carpeta donde se guardarán los archivos en el servidor
   - Puedes usar el botón **"🌐 Explorar..."** para navegar visualmente

6. **¡Descarga!**:
   - Los vídeos se descargarán localmente primero
   - Luego se subirán automáticamente al servidor

## Guardar y Cargar Configuraciones

### Guardar una Nueva Configuración

1. Completa todos los campos SSH
2. Introduce un nombre descriptivo en el campo "Nombre"
3. Haz clic en **"💾 Guardar"**
4. La configuración se guardará en `~/.youtube_downloader/ssh_config.json`

### Cargar una Configuración Guardada

1. Selecciona la configuración del menú desplegable "Configuración:"
2. Haz clic en **"📥 Cargar"** o simplemente selecciónala del menú
3. Los campos se llenarán automáticamente

### Eliminar una Configuración

Las configuraciones se guardan en:
```
~/.youtube_downloader/ssh_config.json
```

Puedes editar este archivo manualmente o eliminarlo para borrar todas las configuraciones.

## Seguridad

⚠️ **Importante**: Las contraseñas se guardan en texto plano en el archivo de configuración.

**Recomendaciones de seguridad**:
- Usa claves SSH en lugar de contraseñas cuando sea posible
- No compartas el archivo `ssh_config.json`
- Considera usar permisos restrictivos: `chmod 600 ~/.youtube_downloader/ssh_config.json`

## Estructura del Archivo de Configuración

Las configuraciones se guardan en `~/.youtube_downloader/ssh_config.json` con esta estructura:

```json
{
  "servers": [
    {
      "name": "Mi Servidor",
      "host": "192.168.1.100",
      "port": 22,
      "username": "usuario",
      "password": "",
      "key_file": "/home/usuario/.ssh/id_rsa",
      "remote_folder": "/home/usuario/Descargas",
      "description": "Servidor SSH personal"
    }
  ]
}
```

⚠️ **Nota**: Este archivo contiene información sensible y se guarda localmente en tu sistema. No se incluye en el repositorio de GitHub.

## Solución de Problemas

### Error de Conexión

- Verifica que el servidor esté encendido y accesible
- Comprueba que el puerto 22 esté abierto
- Verifica usuario y contraseña

### Error al Subir Archivo

- Verifica que la carpeta remota exista o tenga permisos de escritura
- Comprueba el espacio en disco del servidor
- Verifica los permisos del usuario SSH

### La Configuración No Se Guarda

- Verifica que tengas permisos de escritura en `~/.youtube_downloader/`
- Comprueba que el campo "Nombre" no esté vacío
