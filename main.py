#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Punto de entrada principal de la aplicación
Descargador de YouTube - Aplicación de escritorio
"""

import sys
from PySide6.QtWidgets import QApplication

from ui.main_window import YouTubeDownloaderApp
from config import APP_NAME


def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Establecer estilo de la aplicación
    app.setStyle('Fusion')
    app.setApplicationName(APP_NAME)
    
    # Crear y mostrar ventana principal
    window = YouTubeDownloaderApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
