#!/bin/bash
# Script para instalar todas las dependencias del sistema necesarias

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Instalador de Dependencias del Sistema${NC}"
echo "=============================================="
echo ""

# Verificar que se ejecute como root o con sudo
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Este script necesita permisos de administrador${NC}"
    echo "   Ejecutando con sudo..."
    echo ""
    exec sudo bash "$0" "$@"
    exit $?
fi

echo -e "${GREEN}✓${NC} Permisos de administrador confirmados"
echo ""

# Actualizar lista de paquetes
echo -e "${BLUE}🔄 Actualizando lista de paquetes...${NC}"
apt update

echo ""
echo -e "${BLUE}📥 Instalando dependencias del sistema...${NC}"
echo ""

# Instalar FFmpeg
echo -e "${YELLOW}→${NC} Instalando FFmpeg..."
apt install -y ffmpeg

# Instalar dependencias de PySide6/Qt
echo -e "${YELLOW}→${NC} Instalando dependencias de PySide6/Qt..."
apt install -y \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-xinput0 \
    libxcb-xfixes0 \
    libxcb-render0 \
    libxcb-shape0 \
    libxcb-randr0 \
    libxcb-sync1 \
    libxcb-keysyms1 \
    libxcb-image0 \
    libxcb-icccm4 \
    libxcb-shm0 \
    libxcb-util1 \
    libxcb-dri3-0 \
    libxcb-present0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libxrender1 \
    libfontconfig1 \
    libx11-6 \
    libx11-xcb1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2t64

echo ""
echo -e "${GREEN}✅ Todas las dependencias del sistema han sido instaladas${NC}"
echo ""
echo -e "${BLUE}📝 Próximos pasos:${NC}"
echo "   1. Instala las dependencias de Python:"
echo "      pip install -r requirements.txt"
echo ""
echo "   2. Ejecuta la aplicación:"
echo "      ./run.sh"
echo ""
