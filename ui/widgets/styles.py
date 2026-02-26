#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estilos QSS centralizados para la aplicación Media Downloader.
Todos los estilos del tema Matrix se definen aquí para reutilización.
"""

from config import MATRIX_COLORS

_mc = MATRIX_COLORS


def app_stylesheet() -> str:
    """
    Retorna el stylesheet principal de la aplicación.
    Incluye estilos para QMainWindow, QWidget, QGroupBox, QLineEdit,
    QPushButton, QComboBox, QProgressBar, QTextEdit, QRadioButton,
    QLabel, QTabWidget, QTabBar, QScrollArea, QScrollBar, QCheckBox.
    """
    return f"""
        QMainWindow {{
            background-color: {_mc['background']};
            color: {_mc['text']};
        }}
        QWidget {{
            background-color: {_mc['background']};
            color: {_mc['text']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}
        QGroupBox {{
            font-weight: bold;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 15px;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px;
            color: {_mc['accent']};
            font-weight: bold;
        }}
        QLineEdit {{
            padding: 10px;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
            selection-background-color: {_mc['accent_dark']};
            selection-color: {_mc['text_bright']};
        }}
        QLineEdit:focus {{
            border: 1px solid {_mc['accent']};
            background-color: {_mc['background_tertiary']};
        }}
        QLineEdit::placeholder {{
            color: {_mc['text_dim']};
        }}
        QPushButton {{
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11pt;
            background-color: {_mc['background_tertiary']};
            color: {_mc['text']};
            border: 1px solid {_mc['border_dim']};
        }}
        QPushButton:hover {{
            background-color: {_mc['accent_dark']};
            border: 1px solid {_mc['accent']};
            color: {_mc['text_bright']};
        }}
        QPushButton:pressed {{
            background-color: {_mc['background_secondary']};
        }}
        QPushButton:disabled {{
            background-color: {_mc['background']};
            color: {_mc['border_dim']};
            border: 1px solid {_mc['background_tertiary']};
        }}
        QComboBox {{
            padding: 10px;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
        }}
        QComboBox:hover {{
            border: 1px solid {_mc['accent']};
        }}
        QComboBox:focus {{
            border: 1px solid {_mc['accent']};
        }}
        QComboBox::drop-down {{
            border: none;
            background-color: {_mc['background_tertiary']};
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {_mc['text']};
            margin-right: 8px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
            selection-background-color: {_mc['accent_dark']};
            selection-color: {_mc['text_bright']};
            border: 1px solid {_mc['border_dim']};
            outline: none;
        }}
        QProgressBar {{
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            text-align: center;
            height: 28px;
            font-weight: bold;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
        }}
        QProgressBar::chunk {{
            background-color: {_mc['accent']};
            border-radius: 3px;
        }}
        QTextEdit {{
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            background-color: {_mc['background']};
            color: {_mc['text']};
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 10pt;
            selection-background-color: {_mc['accent_dark']};
            selection-color: {_mc['text_bright']};
            padding: 8px;
        }}
        QRadioButton {{
            font-size: 11pt;
            padding: 5px;
            color: {_mc['text']};
            spacing: 8px;
        }}
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid {_mc['border_dim']};
            background-color: {_mc['background_secondary']};
        }}
        QRadioButton::indicator:checked {{
            background-color: {_mc['accent']};
            border: 2px solid {_mc['accent']};
        }}
        QRadioButton::indicator:hover {{
            border: 2px solid {_mc['accent']};
        }}
        QLabel {{
            font-size: 11pt;
            color: {_mc['text']};
        }}
        QTabWidget::pane {{
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            background-color: {_mc['background_secondary']};
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['text_dim']};
            padding: 12px 24px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            border: 1px solid {_mc['border_dim']};
            border-bottom: none;
        }}
        QTabBar::tab:selected {{
            background-color: {_mc['background_secondary']};
            border-bottom: 2px solid {_mc['accent']};
            color: {_mc['accent']};
        }}
        QTabBar::tab:hover {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
        }}
        QScrollArea {{
            border: none;
            background-color: {_mc['background']};
        }}
        QScrollBar:vertical {{
            border: none;
            background-color: {_mc['background_secondary']};
            width: 10px;
            margin: 0;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {_mc['accent_dark']};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {_mc['accent']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar:horizontal {{
            border: none;
            background-color: {_mc['background_secondary']};
            height: 10px;
            margin: 0;
            border-radius: 5px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {_mc['accent_dark']};
            border-radius: 5px;
            min-width: 30px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background-color: {_mc['accent']};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QCheckBox {{
            font-size: 11pt;
            color: {_mc['text']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 2px solid {_mc['border_dim']};
            background-color: {_mc['background_secondary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {_mc['accent']};
            border: 2px solid {_mc['accent']};
        }}
        QCheckBox::indicator:hover {{
            border: 2px solid {_mc['accent']};
        }}
    """


def download_button_style() -> str:
    """Estilo para el boton principal de descarga (verde acentuado)."""
    return f"""
        QPushButton {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
            font-weight: bold;
            padding: 14px 40px;
            font-size: 13pt;
            border: 2px solid {_mc['accent']};
            font-family: 'Consolas', monospace;
        }}
        QPushButton:hover {{
            background-color: {_mc['accent']};
            color: {_mc['background']};
        }}
        QPushButton:disabled {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['border_dim']};
            border: 2px solid {_mc['border_dim']};
        }}
    """


def cancel_button_style() -> str:
    """Estilo para botones de cancelar / limpiar (rojo)."""
    return f"""
        QPushButton {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['error']};
            border: 1px solid {_mc['error']};
        }}
        QPushButton:hover {{
            background-color: #330011;
            color: #FF3366;
        }}
    """


def action_button_style(color_key: str) -> str:
    """
    Estilo generico para botones de accion con color personalizado.

    Args:
        color_key: Clave de MATRIX_COLORS para el color del boton
                   (ej: 'info', 'warning', 'error', 'accent')
    """
    color = _mc.get(color_key, _mc['text'])

    # Mapeo de colores hover segun la clave
    hover_map = {
        'info': ('#003344', '#00EEFF'),
        'warning': ('#332200', '#FFCC00'),
        'error': ('#330011', '#FF3366'),
        'accent': (_mc['accent'], _mc['background']),
    }
    hover_bg, hover_color = hover_map.get(color_key, (_mc['accent_dark'], _mc['text_bright']))

    return f"""
        QPushButton {{
            background-color: {_mc['background_tertiary']};
            color: {color};
            border: 1px solid {color};
        }}
        QPushButton:hover {{
            background-color: {hover_bg};
            color: {hover_color};
        }}
    """


def save_button_style() -> str:
    """Estilo para el boton de guardar configuracion (verde acentuado)."""
    return f"""
        QPushButton {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
            border: 1px solid {_mc['accent']};
        }}
        QPushButton:hover {{
            background-color: {_mc['accent']};
        }}
    """


def select_button_style() -> str:
    """Estilo para el boton de seleccionar en el explorador SSH."""
    return f"""
        QPushButton {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
            font-weight: bold;
            padding: 12px 20px;
            border: 2px solid {_mc['accent']};
        }}
        QPushButton:hover {{
            background-color: {_mc['accent']};
            color: {_mc['background']};
        }}
        QPushButton:disabled {{
            background-color: {_mc['background_tertiary']};
            color: {_mc['border_dim']};
            border: 2px solid {_mc['border_dim']};
        }}
    """


def dialog_stylesheet() -> str:
    """Stylesheet completo para QDialog (explorador SSH, etc.)."""
    return f"""
        QDialog {{
            background-color: {_mc['background']};
            color: {_mc['text']};
        }}
        QLineEdit {{
            padding: 10px;
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            background-color: {_mc['background_secondary']};
            color: {_mc['text']};
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        QLineEdit:focus {{
            border: 1px solid {_mc['accent']};
            background-color: {_mc['background_tertiary']};
        }}
        QPushButton {{
            padding: 10px 18px;
            border-radius: 4px;
            font-weight: bold;
            background-color: {_mc['background_tertiary']};
            color: {_mc['text']};
            border: 1px solid {_mc['border_dim']};
            font-family: 'Consolas', monospace;
        }}
        QPushButton:hover {{
            background-color: {_mc['accent_dark']};
            border: 1px solid {_mc['accent']};
            color: {_mc['text_bright']};
        }}
        QPushButton:pressed {{
            background-color: {_mc['background_secondary']};
        }}
        QTreeWidget {{
            background-color: {_mc['background']};
            color: {_mc['text']};
            border: 1px solid {_mc['border_dim']};
            border-radius: 4px;
            font-size: 11pt;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        QTreeWidget::item {{
            padding: 6px;
        }}
        QTreeWidget::item:selected {{
            background-color: {_mc['accent_dark']};
            color: {_mc['text_bright']};
        }}
        QTreeWidget::item:hover {{
            background-color: {_mc['background_tertiary']};
        }}
        QTreeWidget::branch {{
            background-color: {_mc['background']};
        }}
        QHeaderView::section {{
            background-color: {_mc['background_secondary']};
            color: {_mc['accent']};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {_mc['border_dim']};
            font-weight: bold;
        }}
        QLabel {{
            color: {_mc['text']};
            font-size: 11pt;
            font-family: 'Consolas', monospace;
        }}
        QScrollBar:vertical {{
            border: none;
            background-color: {_mc['background_secondary']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {_mc['accent_dark']};
            border-radius: 5px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {_mc['accent']};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


def valid_field_style() -> str:
    """Estilo para campos de entrada validos (borde verde)."""
    return f"""
        QLineEdit {{
            border: 1px solid {_mc['accent']};
        }}
    """


def invalid_field_style() -> str:
    """Estilo para campos de entrada invalidos (borde rojo)."""
    return f"""
        QLineEdit {{
            border: 1px solid {_mc['error']};
        }}
    """


def neutral_field_style() -> str:
    """Estilo por defecto para campos de entrada (borde dim)."""
    return f"""
        QLineEdit {{
            border: 1px solid {_mc['border_dim']};
        }}
    """
