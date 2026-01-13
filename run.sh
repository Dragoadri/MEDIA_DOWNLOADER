#!/bin/bash
# Script para ejecutar la aplicación Descargador de YouTube

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎬 Descargador de YouTube${NC}"
echo "================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python 3 no está instalado${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python encontrado: $(python3 --version)"

# Verificar FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  Advertencia: FFmpeg no está instalado${NC}"
    echo "   Instálalo con: sudo apt install ffmpeg"
    echo ""
fi

# Verificar dependencias críticas del sistema para PySide6
echo "Verificando dependencias críticas del sistema para PySide6..."

# Lista de dependencias críticas (las más importantes)
CRITICAL_DEPS=(
    "libxcb-cursor0"
    "libxcb-xinerama0"
    "libxcb-xinput0"
    "libxcb-xfixes0"
    "libxcb-render0"
    "libxcb-shape0"
    "libxcb-randr0"
    "libxcb-sync1"
    "libxcb-keysyms1"
    "libxcb-image0"
    "libxcb-icccm4"
    "libxcb-shm0"
    "libxcb-util1"
    "libxcb-dri3-0"
    "libxcb-present0"
    "libxcb-xkb1"
    "libxkbcommon-x11-0"
    "libxkbcommon0"
    "libxrender1"
    "libfontconfig1"
    "libx11-6"
    "libx11-xcb1"
    "libxext6"
    "libxfixes3"
    "libxi6"
    "libxrandr2"
    "libxss1"
    "libxcursor1"
    "libxcomposite1"
)

MISSING_DEPS=()

# Verificar cada dependencia crítica
for dep in "${CRITICAL_DEPS[@]}"; do
    # Verificar si el paquete está instalado
    if ! dpkg -l 2>/dev/null | grep -qE "^ii[[:space:]]+${dep}(:amd64)?[[:space:]]"; then
        MISSING_DEPS+=("$dep")
    fi
done

# Verificar libasound2 (puede ser libasound2t64 en Ubuntu 24.04+)
if ! dpkg -l 2>/dev/null | grep -qE "^ii[[:space:]]+(libasound2|libasound2t64)(:amd64)?[[:space:]]"; then
    MISSING_DEPS+=("libasound2t64")
fi

# Si faltan dependencias, informar al usuario
if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Faltan algunas dependencias del sistema para PySide6${NC}"
    echo "   Las siguientes dependencias son necesarias:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   - $dep"
    done
    echo ""
    echo -e "${YELLOW}💡 Para instalarlas, ejecuta:${NC}"
    echo "   ./install_dependencies.sh"
    echo ""
    echo "   O manualmente:"
    echo "   sudo apt update && sudo apt install -y ${MISSING_DEPS[*]}"
    echo ""
    echo -e "${RED}❌ No se puede continuar sin estas dependencias${NC}"
    exit 1
else
    echo -e "${GREEN}✓${NC} Dependencias críticas del sistema verificadas"
fi

# Verificar si existe entorno virtual
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual encontrado (venv)"
    echo "Activando entorno virtual..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} Entorno virtual encontrado (.venv)"
    echo "Activando entorno virtual..."
    source .venv/bin/activate
fi

# Verificar dependencias
echo "Verificando dependencias..."
MISSING_DEPS=()

if ! python3 -c "import PySide6" 2>/dev/null; then
    MISSING_DEPS+=("PySide6")
fi

if ! python3 -c "import yt_dlp" 2>/dev/null; then
    MISSING_DEPS+=("yt-dlp")
fi

if ! python3 -c "import paramiko" 2>/dev/null; then
    MISSING_DEPS+=("paramiko")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Faltan dependencias de Python: ${MISSING_DEPS[*]}${NC}"
    echo "   Instalando dependencias..."
    pip install -r requirements.txt
fi

echo ""
echo -e "${GREEN}🚀 Iniciando aplicación...${NC}"
echo ""

# Ejecutar aplicación
python3 main.py
