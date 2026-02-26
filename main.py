#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Main entry point for Media Downloader."""

import sys

from PySide6.QtWidgets import QApplication

from config import APP_NAME
from ui.main_window import YouTubeDownloaderApp
from utils.logger import setup_logging


def main():
    setup_logging()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName(APP_NAME)

    window = YouTubeDownloaderApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
