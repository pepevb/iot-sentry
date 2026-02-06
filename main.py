#!/usr/bin/env python3
"""
IoT Sentry - Aplicación Principal

Auditoría de privacidad para dispositivos IoT
100% Local y Privado
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Ajustar path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow


def main():
    """
    Punto de entrada de la aplicación
    """
    # Habilitar High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("IoT Sentry")
    app.setOrganizationName("IoT Sentry")
    app.setApplicationVersion("1.0.0")

    # Aplicar estilo oscuro
    app.setStyle("Fusion")
    from gui.theme import apply_dark_theme
    apply_dark_theme(app)

    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()

    # Ejecutar event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
