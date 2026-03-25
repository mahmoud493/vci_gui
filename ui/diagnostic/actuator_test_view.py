"""ui/diagnostic/actuator_test_view.py — IO Control / actuator test panel."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QSpinBox, QLineEdit, QTextEdit, QFormLayout, QComboBox
)
from PyQt6.QtCore import pyqtSlot
from app.event_bus import bus

COMMON_ACTUATORS = [
    ("Fuel Pump",           0x0180, 0x01),
    ("Engine Fan",          0x0181, 0x01),
    ("A/C Compressor",      0x0182, 0x01),
    ("EGR Valve",           0x0183, 0x01),
    ("Injector Cyl 1",      0x0190, 0x01),
    ("Injector Cyl 2",      0x0191, 0x01),
    ("Injector Cyl 3",      0x0192, 0x01),
    ("Injector Cyl 4",      0x0193, 0x01),
    ("ABS Pump Motor",      0x0200, 0x01),
    ("ABS Valve FL",        0x0201, 0x01),
    ("Throttle Actuator",   0x0220, 0x03),
    ("Cooling Valve",       0x0230, 0x01),
]

class ActuatorTestView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        bus.connection_changed.connect(self._on_connection_changed)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(8)

        # Header
        hdr = QLabel("ACTUATOR TESTS  /  IO CONTROL")
        hdr.setObjectName("label_section")
        root.addWidget(hdr)

        # Quick test grid
        quick_grp = QGroupBox("COMMON ACTUATORS")
        quick_layout = QVBoxLayout(quick_grp)

        for name, did, ctrl_opt in COMMON_ACTUATORS:
            row = QHBoxLayout()
            lbl = QLabel(f"{name}  (DID 0x{did:04X})")
            lbl.setFixedWidth(240)
            row.addWidget(lbl)
            btn_on = QPushButton("ACTIVATE")
            btn_on.setObjectName("btn_success")
            btn_on.setFixedWidth(90)
            btn_on.setProperty("did", did)
            btn_on.setProperty("opt", ctrl_opt)
            btn_on.clicked.connect(lambda _, d=did, o=ctrl_opt: self._activate(d, o))
            row.addWidget(btn_on)
            btn_off = QPushButton("RELEASE")
            btn_off.setObjectName("btn_danger")
            btn_off.setFixedWidth(90)
            btn_off.clicked.connect(lambda _, d=did: self._release(d))
            row.addWidget(btn_off)
            row.addStretch()
            quick_layout.addLayout(row)

        root.addWidget(quick_grp)

        # Manual DID entry
        manual_grp = QGroupBox("MANUAL IO CONTROL")
        manual_form = QFormLayout(manual_grp)
        self._did_edit   = QLineEdit("0x0000")
        self._opt_spin   = QSpinBox()
        self._opt_spin.setRange(0, 255)
        self._opt_spin.setValue(1)
        self._mask_edit  = QLineEdit("")
        self._mask_edit.setPlaceholderText("optional hex bytes e.g. FF 00")
        manual_form.addRow("DID (hex):",          self._did_edit)
        manual_form.addRow("Control Option:",     self._opt_spin)
        manual_form.addRow("Enable Mask (hex):",  self._mask_edit)

        btn_send = QPushButton("SEND IO CONTROL")
        btn_send.setObjectName("btn_primary")
        btn_send.clicked.connect(self._on_manual_send)
        manual_form.addRow("", btn_send)
        root.addWidget(manual_grp)

        # Response display
        resp_grp = QGroupBox("RESPONSE")
        resp_layout = QVBoxLayout(resp_grp)
        self._resp_log = QTextEdit()
        self._resp_log.setReadOnly(True)
        self._resp_log.setFixedHeight(100)
        resp_layout.addWidget(self._resp_log)
        root.addWidget(resp_grp)
        root.addStretch()

        self._setEnabled(False)

    def _setEnabled(self, enabled: bool):
        for child in self.findChildren(QPushButton):
            child.setEnabled(enabled)

    def _activate(self, did: int, opt: int):
        bus.log_message.emit("INFO", f"IO Control ACTIVATE: DID=0x{did:04X} opt=0x{opt:02X}")
        self._resp_log.append(f"→ ACTIVATE DID=0x{did:04X} opt=0x{opt:02X}")

    def _release(self, did: int):
        bus.log_message.emit("INFO", f"IO Control RELEASE: DID=0x{did:04X}")
        self._resp_log.append(f"→ RELEASE DID=0x{did:04X}")

    def _on_manual_send(self):
        try:
            did = int(self._did_edit.text(), 16)
            opt = self._opt_spin.value()
            mask_str = self._mask_edit.text().strip()
            mask = bytes.fromhex(mask_str.replace(" ", "")) if mask_str else b""
            bus.log_message.emit("INFO", f"Manual IO: DID=0x{did:04X} opt={opt} mask={mask.hex()}")
            self._resp_log.append(f"→ Manual DID=0x{did:04X} opt={opt}")
        except ValueError as e:
            bus.log_message.emit("ERROR", f"Invalid input: {e}")

    @pyqtSlot(bool, str)
    def _on_connection_changed(self, connected: bool, _desc: str):
        self._setEnabled(connected)
