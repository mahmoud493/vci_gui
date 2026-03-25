"""ui/widgets/connection_widget.py — Transport connection panel."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QComboBox, QLineEdit, QSpinBox, QStackedWidget, QFormLayout
)
from PyQt6.QtCore import pyqtSlot, Qt
from app.event_bus import bus
from app.state_manager import state
from services.config_service import config
from communication.usb_transport import USBTransport
#from utils.logger import log
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

class ConnectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._transport_obj = None
        self._setup_ui()
        bus.connection_changed.connect(self._on_connection_changed)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(6)

        grp = QGroupBox("TRANSPORT")
        grp_layout = QVBoxLayout(grp)

        # Transport type selector
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("Interface:"))
        self._cbo_type = QComboBox()
        self._cbo_type.addItems(["USB (STM32)", "DoIP (Ethernet)", "J2534 (PassThru)"])
        self._cbo_type.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self._cbo_type)
        grp_layout.addLayout(type_row)

        # Stacked config pages
        self._stack = QStackedWidget()

        # ── USB page ──────────────────────────────────────────────
        usb_page = QWidget()
        usb_form = QFormLayout(usb_page)
        self._usb_port_cbo = QComboBox()
        self._refresh_ports()
        btn_refresh = QPushButton()
        btn_refresh.setIcon(QIcon("resources/icons/refresh.png"))
        # btn_refresh.setIconSize(QSize(20, 20))
        # btn_refresh.setFixedWidth(40)
       
        btn_refresh.clicked.connect(self._refresh_ports)
        port_row = QHBoxLayout()
        port_row.addWidget(self._usb_port_cbo)
        port_row.addWidget(btn_refresh)
        usb_form.addRow("Port:", port_row)
        self._usb_baud = QSpinBox()
        self._usb_baud.setRange(9600, 2000000)
        self._usb_baud.setValue(config.get("usb_baudrate", 115200))
        self._usb_baud.setSingleStep(9600)
        usb_form.addRow("Baud:", self._usb_baud)
        self._stack.addWidget(usb_page)

        # ── DoIP page ─────────────────────────────────────────────
        doip_page = QWidget()
        doip_form = QFormLayout(doip_page)
        self._doip_host = QLineEdit(config.get("doip_host", "192.168.1.1"))
        doip_form.addRow("Host IP:", self._doip_host)
        self._doip_port = QSpinBox()
        self._doip_port.setRange(1, 65535)
        self._doip_port.setValue(config.get("doip_port", 13400))
        doip_form.addRow("Port:", self._doip_port)
        self._doip_src = QLineEdit(f"0x{config.get('doip_src_addr', 0x0E00):04X}")
        doip_form.addRow("Src Addr:", self._doip_src)
        self._doip_tgt = QLineEdit(f"0x{config.get('doip_tgt_addr', 0x0001):04X}")
        doip_form.addRow("Tgt Addr:", self._doip_tgt)
        self._stack.addWidget(doip_page)

        # ── J2534 page ────────────────────────────────────────────
        j2534_page = QWidget()
        j2534_form = QFormLayout(j2534_page)
        self._j2534_dll = QComboBox()
        self._scan_j2534_dlls()
        j2534_form.addRow("Device DLL:", self._j2534_dll)
        self._stack.addWidget(j2534_page)

        grp_layout.addWidget(self._stack)

        # Connect / Disconnect buttons
        btn_row = QHBoxLayout()
        self._btn_connect = QPushButton("CONNECT")
        self._btn_connect.setObjectName("btn_primary")
        self._btn_connect.clicked.connect(self._on_connect)
        self._btn_disconnect = QPushButton("DISCONNECT")
        self._btn_disconnect.setObjectName("btn_danger")
        self._btn_disconnect.setEnabled(False)
        self._btn_disconnect.clicked.connect(self._on_disconnect)
        btn_row.addWidget(self._btn_connect)
        btn_row.addWidget(self._btn_disconnect)
        grp_layout.addLayout(btn_row)

        # Status label
        self._lbl_status = QLabel("● DISCONNECTED")
        self._lbl_status.setObjectName("label_err")
        self._lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grp_layout.addWidget(self._lbl_status)

        root.addWidget(grp)
        root.addStretch()

    def _refresh_ports(self):
        ports = USBTransport.list_ports()
        self._usb_port_cbo.clear()
        self._usb_port_cbo.addItems(ports if ports else ["(no port found)"])

    def _scan_j2534_dlls(self):
        try:
            from communication.j2534_interface import J2534Interface
            devices = J2534Interface.enumerate_devices()
            for name, dll in devices:
                self._j2534_dll.addItem(name, dll)
        except Exception:
            self._j2534_dll.addItem("(not available)")

    @pyqtSlot(int)
    def _on_type_changed(self, idx: int):
        self._stack.setCurrentIndex(idx)

    @pyqtSlot()
    def _on_connect(self):
        idx = self._cbo_type.currentIndex()
        if idx == 0:
            port = self._usb_port_cbo.currentText()
            baud = self._usb_baud.value()
            transport = USBTransport(port=port, baudrate=baud)
            ok = transport.start()
            desc = f"USB {port} @ {baud}"
        elif idx == 1:
            from communication.doip_client import DoIPClient
            host = self._doip_host.text()
            port = self._doip_port.value()
            src  = int(self._doip_src.text(), 16)
            tgt  = int(self._doip_tgt.text(), 16)
            transport = DoIPClient(host, port, src, tgt)
            ok   = transport.connect()
            desc = f"DoIP {host}:{port}"
        else:
            bus.log_message.emit("WARN", "J2534 connect not implemented yet")
            return

        self._transport_obj = transport
        state.connected    = ok
        state.transport_desc = desc
        bus.connection_changed.emit(ok, desc)
        if not ok:
            bus.log_message.emit("ERROR", f"Connection failed: {desc}")

    @pyqtSlot()
    def _on_disconnect(self):
        if self._transport_obj:
            try:
                if hasattr(self._transport_obj, "stop"):
                    self._transport_obj.stop()
                elif hasattr(self._transport_obj, "disconnect"):
                    self._transport_obj.disconnect()
            except Exception:
                pass
            self._transport_obj = None
        state.connected = False
        bus.connection_changed.emit(False, "")

    @pyqtSlot(bool, str)
    def _on_connection_changed(self, connected: bool, desc: str):
        if connected:
            self._lbl_status.setText(f"● CONNECTED  {desc}")
            self._lbl_status.setObjectName("label_ok")
        else:
            self._lbl_status.setText("● DISCONNECTED")
            self._lbl_status.setObjectName("label_err")
        # Force style refresh
        self._lbl_status.style().unpolish(self._lbl_status)
        self._lbl_status.style().polish(self._lbl_status)

        self._btn_connect.setEnabled(not connected)
        self._btn_disconnect.setEnabled(connected)
