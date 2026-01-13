# 🔧 Guía de Instalación Rápida

## ⚠️ Problema Común: Error de Qt Platform Plugin

Si ves este error:
```
qt.qpa.plugin: Could not load the Qt platform plugin "xcb"
```

**Significa que faltan dependencias del sistema para PySide6.**

## ✅ Solución Rápida

### Opción 1: Script Automático (Recomendado)

```bash
./install_dependencies.sh
```

Este script instala automáticamente todas las dependencias necesarias.

### Opción 2: Instalación Manual

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

## 📋 Pasos Completos de Instalación

1. **Instalar dependencias del sistema:**
   ```bash
   ./install_dependencies.sh
   ```

2. **Instalar dependencias de Python:**
   ```bash
   pip install -r requirements.txt
   ```
   
   O si usas entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   ```bash
   ./run.sh
   ```

## 🎯 Orden Correcto

```
1. install_dependencies.sh  ← PRIMERO (dependencias del sistema)
2. pip install -r requirements.txt  ← SEGUNDO (dependencias Python)
3. ./run.sh  ← TERCERO (ejecutar aplicación)
```

¡Listo! 🎉
