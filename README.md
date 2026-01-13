# 🎬 Descargador de YouTube

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Aplicación de escritorio para Ubuntu con interfaz gráfica moderna para descargar contenido de YouTube de forma visual y sencilla**

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [SSH](#-descarga-remota-ssh) • [Estructura](#-estructura-del-proyecto)

</div>

---

## 📸 Vista Previa

![Interfaz de la Aplicación](https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800&h=600&fit=crop)

*Interfaz gráfica intuitiva y moderna*

---

## ✨ Características

<div align="center">

| 🎯 Funcionalidad | 📝 Descripción |
|-----------------|----------------|
| 🎬 **Descarga de Vídeos** | Descarga vídeos completos en formato MP4 |
| 🎵 **Extracción de Audio** | Extrae solo el audio en formato MP3 de alta calidad |
| 🎚️ **Múltiples Calidades** | Elige entre mejor calidad, 1080p, 720p, 480p, 360p, 240p |
| 📊 **Progreso en Tiempo Real** | Barra de progreso con porcentaje y velocidad de descarga |
| 📁 **Selector de Carpeta** | Elige fácilmente dónde guardar tus archivos |
| 💬 **Mensajes Informativos** | Notificaciones claras de éxito y error |
| ⚡ **Sin Bloqueos** | Descarga en segundo plano sin congelar la interfaz |
| 🎨 **Interfaz Moderna** | Diseño limpio y profesional con PySide6 |
| 🌐 **Descarga Remota SSH** | Guarda archivos directamente en tu servidor remoto |
| 💾 **Configuraciones Guardadas** | Guarda y carga configuraciones SSH fácilmente |

</div>

---

## 🚀 Instalación Rápida

### ⚡ Instalación Automática (Recomendado)

Usa nuestro script de instalación que instala todo automáticamente:

```bash
./install_dependencies.sh
```

Este script instala:
- ✅ FFmpeg
- ✅ Todas las dependencias del sistema para PySide6/Qt
- ✅ Librerías X11 necesarias

### 📋 Instalación Manual

#### Paso 1: Instalar Dependencias del Sistema

**⚠️ IMPORTANTE**: PySide6 requiere dependencias del sistema que deben instalarse primero.

```bash
sudo apt update
sudo apt install -y ffmpeg \
    libxcb-cursor0 libxcb-xinerama0 libxcb-xinput0 \
    libxcb-xfixes0 libxcb-render0 libxcb-shape0 \
    libxcb-randr0 libxcb-sync1 libxcb-keysyms1 \
    libxcb-image0 libxcb-icccm4 libxcb-shm0 \
    libxcb-util1 libxcb-dri3-0 libxcb-present0 \
    libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 \
    libxrender1 libfontconfig1 libx11-6 libx11-xcb1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxss1 \
    libxcursor1 libxcomposite1 libasound2t64
```

![System Dependencies](https://img.shields.io/badge/Dependencias%20Sistema-Instaladas-success?style=flat-square)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Instalado-success?style=flat-square)

### Paso 2: Instalar Dependencias de Python

#### Opción A: Instalación Directa (Recomendado para pruebas)

```bash
pip install -r requirements.txt
```

#### Opción B: Usando Entorno Virtual (Recomendado para desarrollo)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

![Python Dependencies](https://img.shields.io/badge/Dependencias-Instaladas-success?style=flat-square)

### Paso 3: Verificar Instalación

Verifica que todo esté correcto:

```bash
python3 --version  # Debe ser 3.8 o superior
ffmpeg -version    # Debe mostrar la versión de FFmpeg
```

---

## 🎮 Cómo Ejecutar la Aplicación

### ⚡ Método Rápido (Recomendado)

Usa el script de ayuda que verifica todo automáticamente:

```bash
./run.sh
```

Este script:
- ✅ Verifica que Python esté instalado
- ✅ Verifica que FFmpeg esté instalado
- ✅ **Verifica las dependencias del sistema para PySide6**
- ✅ Activa el entorno virtual si existe
- ✅ Instala dependencias de Python si faltan
- ✅ Ejecuta la aplicación

> **⚠️ Nota**: Si es la primera vez que ejecutas la aplicación, primero ejecuta `./install_dependencies.sh` para instalar todas las dependencias del sistema.

### Método 1: Ejecución Directa

```bash
python3 main.py
```

### Método 2: Ejecución con Permisos

Si quieres hacer el archivo ejecutable:

```bash
chmod +x main.py
./main.py
```

### Método 3: Desde el Entorno Virtual

Si usas un entorno virtual:

```bash
source venv/bin/activate
python3 main.py
```

---

## 📖 Guía de Uso

### 1️⃣ Introducir URL del Vídeo

![URL Input](https://img.shields.io/badge/Paso-1-blue?style=flat-square)

Pega la URL del vídeo de YouTube en el campo correspondiente. La aplicación acepta URLs de:
- `youtube.com`
- `www.youtube.com`
- `youtu.be`
- `m.youtube.com`

**Ejemplo:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 2️⃣ Seleccionar Formato

![Format Selection](https://img.shields.io/badge/Paso-2-blue?style=flat-square)

Elige el formato de descarga:

- **🎬 Vídeo (MP4)**: Descarga el vídeo completo con audio
- **🎵 Solo Audio (MP3)**: Extrae únicamente el audio en alta calidad (192 kbps)

### 3️⃣ Elegir Calidad (Solo para Vídeo)

![Quality Selection](https://img.shields.io/badge/Paso-3-blue?style=flat-square)

Si elegiste vídeo, selecciona la calidad deseada:

| Calidad | Descripción |
|---------|-------------|
| 🌟 **Mejor calidad disponible** | La máxima calidad que ofrece el vídeo |
| 📺 **1080p** | Full HD |
| 📺 **720p** | HD |
| 📺 **480p** | SD |
| 📺 **360p** | Calidad media |
| 📺 **240p** | Calidad baja |

### 4️⃣ Seleccionar Carpeta de Destino

![Folder Selection](https://img.shields.io/badge/Paso-4-blue?style=flat-square)

Haz clic en **"Buscar..."** para elegir dónde guardar el archivo. Por defecto se usa la carpeta `Descargas` de tu usuario.

### 5️⃣ Iniciar Descarga

![Download Button](https://img.shields.io/badge/Paso-5-green?style=flat-square)

Haz clic en el botón **"Descargar"** (verde) y observa:

- 📊 **Barra de progreso** con porcentaje de descarga
- ⚡ **Velocidad de descarga** en tiempo real
- 💬 **Mensajes informativos** sobre el estado

### 6️⃣ ¡Listo!

![Success](https://img.shields.io/badge/Estado-Completado-success?style=flat-square)

Cuando la descarga termine, recibirás una notificación y el archivo estará en la carpeta seleccionada.

---

## 🌐 Descarga Remota SSH

La aplicación permite descargar vídeos directamente a un servidor remoto mediante SSH.

### Configuración Rápida

1. Ve a la pestaña **"🌐 Servidor SSH"**
2. Completa manualmente los campos:
   - **Host**: IP o dominio de tu servidor (ej: `192.168.1.100`)
   - **Puerto**: `22` (puerto SSH por defecto)
   - **Usuario**: Tu usuario SSH
   - **Contraseña**: Tu contraseña SSH (opcional si usas clave SSH)
   - **Clave SSH**: Ruta a tu archivo de clave privada (opcional, recomendado)
   - **Carpeta remota**: Ruta en el servidor donde guardar (ej: `/home/usuario/Descargas`)

### Guardar Configuraciones

1. Completa los campos SSH
2. Introduce un **nombre** para la configuración
3. Haz clic en **"💾 Guardar"**
4. La próxima vez podrás seleccionarla del menú desplegable

### Probar Conexión

Antes de descargar, puedes probar la conexión con el botón **"🔌 Probar Conexión"**.

### Flujo de Descarga Remota

1. El vídeo se descarga primero a una carpeta temporal local
2. Se establece conexión SSH con el servidor
3. El archivo se sube automáticamente al servidor
4. Se elimina el archivo temporal local

📖 **Más información**: Consulta [CONFIGURACION_SSH.md](CONFIGURACION_SSH.md) para detalles completos.

---

## 📁 Estructura del Proyecto

```
YOUTUBE_DOWNLOAD/
│
├── main.py                 # 🚀 Punto de entrada principal
├── config.py               # ⚙️ Configuración de la aplicación
├── requirements.txt        # 📦 Dependencias
├── README.md              # 📖 Este archivo
│
├── ui/                     # 🎨 Módulo de interfaz de usuario
│   ├── __init__.py
│   └── main_window.py     # Ventana principal
│
├── download/               # ⬇️ Módulo de descarga
│   ├── __init__.py
│   ├── downloader.py      # Lógica de descarga
│   └── progress_hook.py   # Hook de progreso
│
├── utils/                  # 🛠️ Utilidades
│   ├── __init__.py
│   ├── validators.py      # Validación de entradas
│   ├── ssh_client.py      # Cliente SSH para servidores remotos
│   └── config_manager.py  # Gestor de configuraciones SSH
│
├── scripts/                # 📜 Scripts de ayuda
│   └── README.md          # Documentación de scripts
│
├── config/                 # ⚙️ Archivos de configuración
│   └── ssh_config.example.json  # Ejemplo de configuración SSH
│
├── run.sh                  # ⚡ Script de ejecución rápida
├── install_dependencies.sh # 📦 Script de instalación de dependencias
├── CONFIGURACION_SSH.md    # 🔐 Guía de configuración SSH
└── INSTALACION.md          # 📋 Guía de instalación
```

### 📚 Descripción de Módulos

| Módulo | Responsabilidad |
|--------|----------------|
| `main.py` | Inicializa la aplicación Qt y muestra la ventana principal |
| `config.py` | Contiene todas las constantes y configuraciones |
| `ui/main_window.py` | Interfaz gráfica completa con todos los widgets |
| `download/downloader.py` | Maneja la lógica de descarga con yt-dlp |
| `download/progress_hook.py` | Captura y reporta el progreso de descarga |
| `utils/validators.py` | Valida URLs y rutas de carpetas |
| `utils/ssh_client.py` | Cliente SSH para conexión y transferencia remota |
| `utils/config_manager.py` | Gestor para guardar/cargar configuraciones SSH |
| `run.sh` | Script de ejecución con verificación de dependencias |
| `install_dependencies.sh` | Script de instalación de dependencias del sistema |

---

## 🔧 Requisitos del Sistema

### Requisitos Mínimos

- **Sistema Operativo**: Ubuntu 18.04 o superior (o cualquier distribución Linux)
- **Python**: 3.8 o superior
- **FFmpeg**: Última versión estable
- **RAM**: 512 MB mínimo
- **Espacio en disco**: 100 MB para la aplicación + espacio para descargas

### Dependencias de Python

```
PySide6>=6.5.0    # Interfaz gráfica Qt
yt-dlp>=2023.7.6  # Descarga de contenido de YouTube
paramiko>=3.0.0   # Cliente SSH para descarga remota
```

---

## 🔒 Seguridad y Privacidad

### ⚠️ Información Importante

- **Las configuraciones SSH se guardan localmente** en `~/.youtube_downloader/`
- **Las contraseñas se almacenan en texto plano** en el archivo de configuración
- **Ningún dato sensible se incluye en el repositorio** de GitHub
- Los archivos de configuración local están excluidos mediante `.gitignore`

### 🛡️ Recomendaciones de Seguridad

1. **Usa claves SSH en lugar de contraseñas** cuando sea posible
2. **Protege tus archivos de configuración**:
   ```bash
   chmod 600 ~/.youtube_downloader/ssh_config.json
   chmod 600 ~/.youtube_downloader/app_settings.json
   ```
3. **No compartas tus archivos de configuración** con otros usuarios
4. **No subas archivos de configuración** a repositorios públicos

### 📁 Ubicación de Archivos de Configuración

Todos los archivos de configuración se guardan en:
```
~/.youtube_downloader/
├── ssh_config.json      # Configuraciones SSH guardadas
└── app_settings.json    # Configuraciones de la aplicación
```

Estos archivos **NO se incluyen** en el repositorio de GitHub.

---

## 🐛 Solución de Problemas

### ❌ Error: "Could not load the Qt platform plugin 'xcb'"

**Este es el error más común en Ubuntu.** Faltan dependencias del sistema para PySide6.

**Solución rápida:**
```bash
./install_dependencies.sh
```

**O manualmente:**
```bash
sudo apt update
sudo apt install -y libxcb-cursor0 libxcb-xinerama0 libxcb-xinput0 \
    libxcb-xfixes0 libxcb-render0 libxcb-shape0 libxcb-randr0 \
    libxcb-sync1 libxcb-keysyms1 libxcb-image0 libxcb-icccm4 \
    libxcb-shm0 libxcb-util1 libxcb-dri3-0 libxcb-present0 \
    libxcb-xkb1 libxkbcommon-x11-0 libxkbcommon0 libxrender1 \
    libfontconfig1 libx11-6 libx11-xcb1 libxext6 libxfixes3 \
    libxi6 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2t64
```

### ❌ Error: "FFmpeg no encontrado"

**Solución:**
```bash
sudo apt update
sudo apt install ffmpeg -y
```

Verifica la instalación:
```bash
ffmpeg -version
```

### ❌ Error: "No se puede descargar el vídeo"

**Posibles causas y soluciones:**

1. **URL inválida**: Verifica que la URL sea correcta y completa
2. **Restricciones geográficas**: Algunos vídeos pueden estar bloqueados en tu región
3. **Vídeo privado o eliminado**: El vídeo puede no estar disponible
4. **Conexión a internet**: Verifica tu conexión

### ❌ Error: "No se puede crear la carpeta"

**Solución:**
- Verifica que tengas permisos de escritura en la ubicación seleccionada
- Intenta seleccionar otra carpeta (por ejemplo, tu carpeta de usuario)

### ❌ La aplicación no inicia

**Verificaciones:**

1. **Python instalado:**
   ```bash
   python3 --version
   ```

2. **Dependencias instaladas:**
   ```bash
   pip list | grep -E "PySide6|yt-dlp"
   ```

3. **Permisos de ejecución:**
   ```bash
   chmod +x main.py
   ```

### ❌ Error de importación de módulos

**Solución:**
Asegúrate de ejecutar la aplicación desde el directorio raíz del proyecto:

```bash
cd "/home/drago/Escritorio/MY PROYECTS/YOUTUBE_DOWNLOAD"
python3 main.py
```

---

## 🎯 Características Técnicas

### Arquitectura

- **Patrón MVC**: Separación clara entre interfaz, lógica y datos
- **Hilos**: Descargas en segundo plano sin bloquear la UI
- **Señales Qt**: Comunicación asíncrona entre hilos y UI
- **Módulos**: Código organizado y mantenible

### Tecnologías Utilizadas

<div align="center">

![PySide6](https://img.shields.io/badge/PySide6-6.5+-41CD52?style=flat-square&logo=qt&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-2023.7.6+-FF0000?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)

</div>

---

## 📝 Notas Importantes

- ⚠️ **Respeto a los derechos de autor**: Solo descarga contenido que tengas permiso para descargar
- 💾 **Espacio en disco**: Los vídeos en alta calidad ocupan mucho espacio
- 🌐 **Conexión estable**: Se recomienda una conexión estable para descargas grandes
- 🔄 **Actualizaciones**: Mantén yt-dlp actualizado para mejor compatibilidad:
  ```bash
  pip install --upgrade yt-dlp
  ```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si encuentras algún bug o tienes una sugerencia:

1. Abre un issue describiendo el problema
2. Propón mejoras o nuevas funcionalidades
3. Contribuye con código siguiendo la estructura del proyecto

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso personal y educativo.

---

## 🙏 Agradecimientos

- **yt-dlp**: Por la excelente herramienta de descarga
- **Qt/PySide6**: Por el framework de interfaz gráfica
- **Python**: Por ser un lenguaje tan versátil

---

<div align="center">

**Hecho con ❤️ para la comunidad de Ubuntu**

![Made with Love](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

</div>
