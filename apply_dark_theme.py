# apply_dark_theme.py
# Applies a dark theme to the PyQt5 application, configuring colors and styles for various GUI elements to achieve a consistent dark appearance.

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

def apply_dark_theme(app):
    app.setStyle("Fusion")

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    
    # Set the style for QDoubleSpinBox and QDockWidget title bar buttons
    app.setStyleSheet("""
    QDockWidget::close-button, QDockWidget::float-button {
        border: none;
        background: #333;
        padding: 2px;
    }
    QDockWidget::close-button:hover, QDockWidget::float-button:hover {
        background: #555;
    }
    QDockWidget::close-button:pressed, QDockWidget::float-button:pressed {
        background: #777;
    }
    """)