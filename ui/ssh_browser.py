#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Explorador de archivos remoto SSH
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from utils.ssh_client import SSHClient
from ui.widgets.styles import select_button_style, cancel_button_style, action_button_style


class SSHBrowserDialog(QDialog):
    """Diálogo para explorar carpetas remotas por SSH"""

    def __init__(self, parent=None, ssh_config=None):
        """
        Inicializa el explorador SSH

        Args:
            parent: Widget padre
            ssh_config: Diccionario con configuración SSH (host, port, username, password, key_file)
        """
        super().__init__(parent)
        self.ssh_config = ssh_config
        self.ssh_client = None
        self.selected_path = None
        self.current_path = "/"

        self.setWindowTitle(">> SSH FILE BROWSER")
        self.setMinimumSize(650, 550)
        self.init_ui()
        self.apply_matrix_theme()

        if ssh_config:
            self.connect_and_load()

    def apply_matrix_theme(self):
        """Aplica el tema Matrix al diálogo usando estilos centralizados"""
        from ui.widgets.styles import dialog_stylesheet
        self.setStyleSheet(dialog_stylesheet())
    
    def init_ui(self):
        """Inicializa la interfaz del explorador"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Barra de navegación
        nav_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setText(self.current_path)
        self.path_input.setPlaceholderText("/home/usuario/...")
        self.path_input.returnPressed.connect(self.navigate_to_path)

        nav_button = QPushButton("IR")
        nav_button.clicked.connect(self.navigate_to_path)

        home_button = QPushButton("HOME")
        home_button.clicked.connect(self.go_home)

        nav_layout.addWidget(QLabel("Ruta:"))
        nav_layout.addWidget(self.path_input)
        nav_layout.addWidget(nav_button)
        nav_layout.addWidget(home_button)

        layout.addLayout(nav_layout)

        # Árbol de directorios
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel(">> DIRECTORIOS")
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.tree)

        # Botones
        buttons_layout = QHBoxLayout()

        self.select_button = QPushButton(">> SELECCIONAR")
        self.select_button.setStyleSheet(select_button_style())
        self.select_button.clicked.connect(self.accept_selection)
        self.select_button.setEnabled(False)

        cancel_button = QPushButton("CANCELAR")
        cancel_button.setStyleSheet(cancel_button_style())
        cancel_button.clicked.connect(self.reject)

        refresh_button = QPushButton("ACTUALIZAR")
        refresh_button.setStyleSheet(action_button_style('info'))
        refresh_button.clicked.connect(self.refresh_current_directory)
        
        buttons_layout.addWidget(refresh_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(self.select_button)
        
        layout.addLayout(buttons_layout)
    
    def connect_and_load(self):
        """Conecta al servidor SSH y carga el directorio raíz"""
        if not self.ssh_config:
            QMessageBox.warning(self, "Error", "No hay configuración SSH disponible")
            return
        
        try:
            self.ssh_client = SSHClient()
            success, message = self.ssh_client.connect(
                self.ssh_config['host'],
                self.ssh_config['port'],
                self.ssh_config['username'],
                self.ssh_config.get('password'),
                self.ssh_config.get('key_file')
            )
            
            if not success:
                QMessageBox.critical(self, "Error de Conexión", message)
                return
            
            # Obtener el directorio home del usuario
            stdin, stdout, stderr = self.ssh_client.client.exec_command('echo $HOME')
            home_dir = stdout.read().decode().strip()
            if home_dir:
                self.current_path = home_dir
                self.path_input.setText(self.current_path)
            
            self.load_directory(self.current_path)
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al conectar: {str(e)}")
    
    def load_directory(self, path):
        """Carga el contenido de un directorio"""
        if not self.ssh_client:
            return
        
        try:
            # Limpiar árbol
            self.tree.clear()
            
            # Listar directorio
            success, items, message = self.ssh_client.list_directory(path)
            
            if not success:
                QMessageBox.warning(self, "Error", message)
                return
            
            # Añadir item para subir un nivel
            if path != "/":
                parent_item = QTreeWidgetItem(self.tree)
                parent_item.setText(0, "[..] Parent Directory")
                parent_item.setData(0, Qt.UserRole, "..")
            
            # Añadir carpetas
            for item in sorted(items):
                item_path = f"{path.rstrip('/')}/{item}" if path != "/" else f"/{item}"
                
                # Verificar si es directorio
                try:
                    stat = self.ssh_client.sftp.stat(item_path)
                    if stat.st_mode & 0o040000:  # Es un directorio
                        tree_item = QTreeWidgetItem(self.tree)
                        tree_item.setText(0, f"[DIR] {item}")
                        tree_item.setData(0, Qt.UserRole, item_path)
                except:
                    pass
            
            self.current_path = path
            self.path_input.setText(path)
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar directorio: {str(e)}")
    
    def on_item_double_clicked(self, item, column):
        """Se ejecuta al hacer doble clic en un item"""
        path = item.data(0, Qt.UserRole)
        if path == "..":
            # Subir un nivel
            parent_path = "/".join(self.current_path.rstrip("/").split("/")[:-1])
            if not parent_path:
                parent_path = "/"
            self.load_directory(parent_path)
        else:
            # Entrar en el directorio
            self.load_directory(path)
    
    def on_item_clicked(self, item, column):
        """Se ejecuta al hacer clic en un item"""
        path = item.data(0, Qt.UserRole)
        if path and path != "..":
            self.selected_path = path
            self.path_input.setText(path)
            self.select_button.setEnabled(True)
        else:
            self.select_button.setEnabled(False)
    
    def navigate_to_path(self):
        """Navega a la ruta especificada en el campo de texto"""
        path = self.path_input.text().strip()
        if path:
            self.load_directory(path)
    
    def go_home(self):
        """Va al directorio home del usuario"""
        if self.ssh_client:
            try:
                stdin, stdout, stderr = self.ssh_client.client.exec_command('echo $HOME')
                home_dir = stdout.read().decode().strip()
                if home_dir:
                    self.load_directory(home_dir)
            except:
                self.load_directory("/home")
        else:
            self.load_directory("/home")
    
    def refresh_current_directory(self):
        """Actualiza el directorio actual"""
        self.load_directory(self.current_path)
    
    def accept_selection(self):
        """Acepta la selección y cierra el diálogo"""
        selected_path = self.path_input.text().strip()
        if selected_path:
            self.selected_path = selected_path
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Por favor, selecciona una carpeta")
    
    def get_selected_path(self):
        """Retorna la ruta seleccionada"""
        return self.selected_path
    
    def closeEvent(self, event):
        """Cierra la conexión SSH al cerrar el diálogo"""
        if self.ssh_client:
            self.ssh_client.disconnect()
        event.accept()
