#!/bin/bash
# ============================================================================
#  MEDIA DOWNLOADER - INSTALADOR DE DEPENDENCIAS
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

# Funciones de impresión estilo Matrix
print_matrix_header() {
    echo -e "${BRIGHT_GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                                                                              ║"
    echo "║   ███╗   ███╗███████╗██████╗ ██╗ █████╗     ██████╗ ██╗                     ║"
    echo "║   ████╗ ████║██╔════╝██╔══██╗██║██╔══██╗    ██╔══██╗██║                     ║"
    echo "║   ██╔████╔██║█████╗  ██║  ██║██║███████║    ██║  ██║██║                     ║"
    echo "║   ██║╚██╔╝██║██╔══╝  ██║  ██║██║██╔══██║    ██║  ██║██║                     ║"
    echo "║   ██║ ╚═╝ ██║███████╗██████╔╝██║██║  ██║    ██████╔╝███████╗                ║"
    echo "║   ╚═╝     ╚═╝╚══════╝╚═════╝ ╚═╝╚═╝  ╚═╝    ╚═════╝ ╚══════╝                ║"
    echo "║                                                                              ║"
    echo "║                    >> INSTALADOR DE DEPENDENCIAS <<                          ║"
    echo "║                          [ VERSION 2.0 ]                                     ║"
    echo "║                                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_step() {
    echo -e "${BRIGHT_GREEN}[>>]${NC} ${GREEN}$1${NC}"
}

print_success() {
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

print_separator() {
    echo -e "${DARK_GREEN}────────────────────────────────────────────────────────────────────────────────${NC}"
}

# Mostrar header
clear
print_matrix_header

echo ""
print_separator
echo ""

# Verificar que se ejecute como root o con sudo
if [ "$EUID" -ne 0 ]; then
    print_warning "Este script necesita permisos de administrador"
    print_info "Ejecutando con sudo..."
    echo ""
    exec sudo bash "$0" "$@"
    exit $?
fi

print_success "Permisos de administrador confirmados"
echo ""
print_separator
echo ""

# ============================================================================
# PASO 1: Actualizar sistema
# ============================================================================
print_step "PASO 1/5: Actualizando lista de paquetes..."
echo ""

apt update -qq
if [ $? -eq 0 ]; then
    print_success "Lista de paquetes actualizada"
else
    print_error "Error al actualizar paquetes"
    exit 1
fi

echo ""
print_separator
echo ""

# ============================================================================
# PASO 2: Instalar Python y herramientas básicas
# ============================================================================
print_step "PASO 2/5: Instalando Python y herramientas básicas..."
echo ""

apt install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    curl \
    wget

if [ $? -eq 0 ]; then
    print_success "Python y herramientas básicas instaladas"
else
    print_error "Error al instalar Python"
    exit 1
fi

echo ""
print_separator
echo ""

# ============================================================================
# PASO 3: Instalar FFmpeg
# ============================================================================
print_step "PASO 3/5: Instalando FFmpeg (procesamiento de audio/video)..."
echo ""

apt install -y -qq ffmpeg

if [ $? -eq 0 ]; then
    print_success "FFmpeg instalado correctamente"
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1)
    print_info "$FFMPEG_VERSION"
else
    print_error "Error al instalar FFmpeg"
    exit 1
fi

echo ""
print_separator
echo ""

# ============================================================================
# PASO 4: Instalar dependencias de Qt/PySide6
# ============================================================================
print_step "PASO 4/5: Instalando dependencias de Qt/PySide6..."
echo ""

apt install -y -qq \
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
    libegl1 \
    libgl1 \
    libglib2.0-0

# Intentar instalar libasound (puede variar el nombre según la versión)
apt install -y -qq libasound2t64 2>/dev/null || apt install -y -qq libasound2 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "Dependencias de Qt instaladas correctamente"
else
    print_warning "Algunas dependencias de Qt podrían no haberse instalado"
fi

echo ""
print_separator
echo ""

# ============================================================================
# PASO 5: Instalar dependencias de Python
# ============================================================================
print_step "PASO 5/5: Instalando dependencias de Python..."
echo ""

# Obtener el directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if [ -f "$REQUIREMENTS_FILE" ]; then
    # Crear entorno virtual si no existe
    VENV_DIR="$SCRIPT_DIR/.venv"

    if [ ! -d "$VENV_DIR" ]; then
        print_info "Creando entorno virtual..."
        python3 -m venv "$VENV_DIR"
    fi

    # Remove old venv if .venv exists
    if [ -d "$SCRIPT_DIR/venv" ] && [ -d "$VENV_DIR" ]; then
        rm -rf "$SCRIPT_DIR/venv"
        print_info "Eliminado entorno virtual antiguo (venv/)"
    fi

    # Activar entorno virtual e instalar dependencias
    print_info "Instalando dependencias de Python en entorno virtual..."
    source "$VENV_DIR/bin/activate"

    pip install --upgrade pip -q
    pip install -r "$REQUIREMENTS_FILE" -q

    if [ $? -eq 0 ]; then
        print_success "Dependencias de Python instaladas correctamente"
    else
        print_warning "Algunas dependencias de Python podrían no haberse instalado"
        print_info "Intenta instalarlas manualmente con: pip install -r requirements.txt"
    fi

    deactivate
else
    print_warning "No se encontró requirements.txt"
    print_info "Instala las dependencias manualmente con: pip install -r requirements.txt"
fi

echo ""
print_separator
echo ""

# ============================================================================
# RESUMEN FINAL
# ============================================================================
echo -e "${BRIGHT_GREEN}"
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                      >> INSTALACION COMPLETADA <<                            ║"
echo "║                                                                              ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║                                                                              ║"
echo "║   [OK] Dependencias del sistema instaladas                                   ║"
echo "║   [OK] FFmpeg instalado                                                      ║"
echo "║   [OK] Dependencias de Qt/PySide6 instaladas                                ║"
echo "║   [OK] Entorno virtual creado                                               ║"
echo "║   [OK] Dependencias de Python instaladas                                    ║"
echo "║                                                                              ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║                                                                              ║"
echo "║   >> PARA EJECUTAR LA APLICACION:                                           ║"
echo "║                                                                              ║"
echo "║      source venv/bin/activate                                               ║"
echo "║      python3 main.py                                                        ║"
echo "║                                                                              ║"
echo "║   >> O USA EL SCRIPT:                                                       ║"
echo "║                                                                              ║"
echo "║      ./run.sh                                                               ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
