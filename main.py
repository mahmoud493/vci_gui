# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 13:07:18 2026

@author: IT DOCTOR
"""
"""main.py — VCI PRO application entry point."""
import sys
import os

# Ensure project root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore    import Qt
from PyQt6.QtGui     import QFont

from ui.main_window              import MainWindow
from app.app_controller          import AppController
from services.logging_service    import install_gui_log_handler
from utils.logger                import log
from utils.constants             import APP_NAME, APP_VERSION

def load_stylesheet(app: QApplication) -> None:
    style_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "dark.qss")
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        log.debug("Stylesheet loaded")
    except FileNotFoundError:
        log.warning("Stylesheet not found — using default style")

def main():
    # High-DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Font
    font = QFont("Consolas", 10)
    app.setFont(font)

    load_stylesheet(app)

    # Route Python log to GUI console
    #install_gui_log_handler()

    # Core controller (must exist before window to wire signals)
    controller = AppController()  # noqa: F841  (kept alive)

    window = MainWindow()
    window.show()
    # ✅ Installer après création UI
   
    install_gui_log_handler("vci_pro")
    log.info(f"{APP_NAME} v{APP_VERSION} started")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
