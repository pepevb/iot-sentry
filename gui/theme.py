"""
IoT Sentry - Tema Visual (Dark Mode)
"""

from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt


def apply_dark_theme(app):
    """
    Aplicar tema oscuro a la aplicación

    Args:
        app: QApplication
    """
    # Crear paleta oscura
    palette = QPalette()

    # Colores base
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(35, 35, 35))

    # Colores deshabilitados
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                    QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,
                    QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                    QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight,
                    QColor(80, 80, 80))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText,
                    QColor(127, 127, 127))

    app.setPalette(palette)

    # Stylesheet adicional para widgets específicos
    stylesheet = """
    QToolTip {
        color: #ffffff;
        background-color: #2a82da;
        border: 1px solid white;
    }

    QPushButton {
        background-color: #2a82da;
        border: none;
        color: white;
        padding: 8px 16px;
        border-radius: 4px;
    }

    QPushButton:hover {
        background-color: #3a92ea;
    }

    QPushButton:pressed {
        background-color: #1a72ca;
    }

    QPushButton:disabled {
        background-color: #555555;
        color: #888888;
    }

    QTableWidget {
        gridline-color: #555555;
        selection-background-color: #2a82da;
    }

    QTableWidget::item:selected {
        background-color: #2a82da;
    }

    QHeaderView::section {
        background-color: #3a3a3a;
        padding: 4px;
        border: 1px solid #555555;
        font-weight: bold;
    }

    QTabWidget::pane {
        border: 1px solid #555555;
    }

    QTabBar::tab {
        background-color: #3a3a3a;
        color: white;
        padding: 8px 16px;
        border: 1px solid #555555;
    }

    QTabBar::tab:selected {
        background-color: #2a82da;
    }

    QProgressBar {
        border: 1px solid #555555;
        border-radius: 4px;
        text-align: center;
    }

    QProgressBar::chunk {
        background-color: #2a82da;
    }

    QStatusBar {
        background-color: #2a2a2a;
    }
    """

    app.setStyleSheet(stylesheet)


# Colores de severidad para alertas
SEVERITY_COLORS = {
    'low': '#FFA500',      # Orange
    'medium': '#FF8C00',   # Dark Orange
    'high': '#FF4500',     # Red Orange
}

# Colores de estado
STATUS_COLORS = {
    'online': '#00FF00',   # Green
    'offline': '#808080',  # Gray
    'warning': '#FFFF00',  # Yellow
}
