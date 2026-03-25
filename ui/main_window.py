"""ui/main_window.py — Application main window."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTabWidget, QSplitter, QLabel, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QFont

from ui.dashboard.dashboard_view     import DashboardView
from ui.diagnostic.diag_panel        import DiagPanel
from ui.network.bus_monitor          import BusMonitor
from ui.widgets.log_console          import LogConsole
from ui.widgets.connection_widget    import ConnectionWidget
from ui.widgets.status_bar           import VCIStatusBar
from app.event_bus                   import bus
from utils.constants                 import APP_NAME, APP_VERSION

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  v{APP_VERSION}  —  Automotive VCI Interface")
        self.setMinimumSize(QSize(1280, 800))
        self._build_menu()
        self._build_ui()
        self.setStatusBar(VCIStatusBar(self))

    # ── Menu ──────────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        act_save_log = QAction("Save Log...", self)
        act_save_log.setShortcut("Ctrl+S")
        act_save_log.triggered.connect(self._save_log)
        file_menu.addAction(act_save_log)
        file_menu.addSeparator()
        act_quit = QAction("Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        view_menu = mb.addMenu("View")
        act_toggle_log = QAction("Toggle Console", self)
        act_toggle_log.setShortcut("Ctrl+L")
        act_toggle_log.triggered.connect(self._toggle_console)
        view_menu.addAction(act_toggle_log)

        diag_menu = mb.addMenu("Diagnostic")
        act_scan  = QAction("Scan ECUs", self)
        act_scan.setShortcut("F5")
        diag_menu.addAction(act_scan)
        act_read_dtc = QAction("Read DTCs", self)
        act_read_dtc.setShortcut("F6")
        diag_menu.addAction(act_read_dtc)

        help_menu = mb.addMenu("Help")
        act_about = QAction("About VCI PRO", self)
        act_about.triggered.connect(self._about)
        help_menu.addAction(act_about)

    # ── Central widget ────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # ── Left sidebar: connection ───────────────────────────────
        sidebar = QWidget()
        sidebar.setFixedWidth(280)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(APP_NAME)
        title_lbl.setObjectName("label_title")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(title_lbl)

        ver_lbl = QLabel(f"v{APP_VERSION}  |  STM32H723 VCI")
        ver_lbl.setObjectName("label_section")
        ver_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb_layout.addWidget(ver_lbl)

        sb_layout.addSpacing(8)
        sb_layout.addWidget(ConnectionWidget())

        root.addWidget(sidebar)

        # ── Main area ─────────────────────────────────────────────
        main_splitter = QSplitter(Qt.Orientation.Vertical)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.addTab(DashboardView(),  "DASHBOARD")
        self._tabs.addTab(DiagPanel(),      "DIAGNOSTIC")
        self._tabs.addTab(BusMonitor(),     "BUS MONITOR")
        main_splitter.addWidget(self._tabs)

        # Console
        self._console = LogConsole()
        self._console.setFixedHeight(160)
        main_splitter.addWidget(self._console)

        main_splitter.setStretchFactor(0, 4)
        main_splitter.setStretchFactor(1, 1)
        root.addWidget(main_splitter)

    def _toggle_console(self):
        self._console.setVisible(not self._console.isVisible())

    def _save_log(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Log", "vci_log.txt", "Text Files (*.txt)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._console._log.toPlainText())
            bus.log_message.emit("INFO", f"Log saved: {path}")

    def _about(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br><br>"
            "Professional Automotive VCI Interface<br>"
            "Target: STM32H723VGT6 @ 550 MHz<br>"
            "Protocols: CAN-FD · LIN · K-Line · DoIP · UDS<br><br>"
            "Built with PyQt6"
        )

    def closeEvent(self, event):
        from services.config_service import config
        config.save()
        bus.log_message.emit("INFO", "Application closing — config saved")
        super().closeEvent(event)
