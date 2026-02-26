#!/bin/bash
# ============================================================================
#  MEDIA DOWNLOADER - SCRIPT DE EJECUCION
#  Version 2.0 - Matrix Edition
# ============================================================================

# Colores Matrix
GREEN='\033[0;32m'
BRIGHT_GREEN='\033[1;32m'
DARK_GREEN='\033[2;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones
print_header() {
    echo -e "${BRIGHT_GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║          >> MEDIA DOWNLOADER v2.0 <<                        ║"
    echo "║              [ MATRIX EDITION ]                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_ok() {
    echo -e "${BRIGHT_GREEN}[OK]${NC} ${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}[!!]${NC} ${RED}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[??]${NC} ${YELLOW}$1${NC}"
}

print_info() {
    echo -e "${CYAN}[--]${NC} ${CYAN}$1${NC}"
}

print_step() {
    echo -e "${BRIGHT_GREEN}[>>]${NC} ${GREEN}$1${NC}"
}

# Mostrar header
clear
print_header
echo ""

# ============================================================================
# VERIFICACIONES
# ============================================================================

# Verificar Python
print_step "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    echo ""
    print_info "Instala Python con: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
print_ok "$PYTHON_VERSION"

# Verificar FFmpeg
print_step "Verificando FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    print_warning "FFmpeg no está instalado"
    print_info "Algunas funciones podrían no funcionar correctamente"
    print_info "Instala con: sudo apt install ffmpeg"
else
    print_ok "FFmpeg disponible"
fi

# Verificar dependencias críticas del sistema para PySide6
print_step "Verificando dependencias del sistema..."

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
    "libxcb-xkb1"
    "libxkbcommon-x11-0"
    "libxkbcommon0"
)

MISSING_SYS_DEPS=()

for dep in "${CRITICAL_DEPS[@]}"; do
    if ! dpkg -l 2>/dev/null | grep -qE "^ii[[:space:]]+${dep}(:amd64)?[[:space:]]"; then
        MISSING_SYS_DEPS+=("$dep")
    fi
done

if [ ${#MISSING_SYS_DEPS[@]} -gt 0 ]; then
    print_warning "Faltan dependencias del sistema"
    print_info "Ejecuta: ./install_dependencies.sh"
    echo ""
    print_error "No se puede continuar sin las dependencias"
    exit 1
else
    print_ok "Dependencias del sistema verificadas"
fi

# Activar entorno virtual
print_step "Buscando entorno virtual..."

if [ -d ".venv" ]; then
    print_ok "Entorno virtual encontrado (.venv)"
    source .venv/bin/activate
elif [ -d "venv" ]; then
    print_ok "Entorno virtual encontrado (venv)"
    source venv/bin/activate
else
    print_warning "No se encontro entorno virtual"
    print_info "Creando entorno virtual..."
    python3 -m venv .venv
    source .venv/bin/activate
    print_ok "Entorno virtual creado y activado"
fi

# Verificar dependencias de Python
print_step "Verificando dependencias de Python..."

MISSING_PY_DEPS=()

if ! python3 -c "import PySide6" 2>/dev/null; then
    MISSING_PY_DEPS+=("PySide6")
fi

if ! python3 -c "import yt_dlp" 2>/dev/null; then
    MISSING_PY_DEPS+=("yt-dlp")
fi

if ! python3 -c "import paramiko" 2>/dev/null; then
    MISSING_PY_DEPS+=("paramiko")
fi

if [ ${#MISSING_PY_DEPS[@]} -gt 0 ]; then
    print_warning "Faltan dependencias: ${MISSING_PY_DEPS[*]}"
    print_info "Instalando dependencias..."
    pip install -r requirements.txt -q
    print_ok "Dependencias instaladas"
else
    print_ok "Todas las dependencias de Python disponibles"
fi

echo ""

# ============================================================================
# EJECUTAR APLICACION
# ============================================================================

echo -e "${BRIGHT_GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║               >> INICIANDO APLICACION <<                     ║"
echo "║                                                              ║"
echo "║   Wake up, Neo...                                           ║"
echo "║   The Matrix has you...                                     ║"
echo "║   Follow the white rabbit.                                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Ejecutar aplicación
python3 main.py

# Mensaje de cierre
echo ""
echo -e "${BRIGHT_GREEN}[>>]${NC} ${GREEN}Aplicación cerrada${NC}"
echo ""
