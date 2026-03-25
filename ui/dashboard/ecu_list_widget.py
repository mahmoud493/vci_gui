"""ui/dashboard/ecu_list_widget.py — ECU list with scan button."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from models.ecu import ECU, ECUStatus
from app.event_bus import bus

STATUS_COLORS = {
    ECUStatus.PRESENT:  "#00e676",
    ECUStatus.ACTIVE:   "#00d4ff",
    ECUStatus.NO_RESP:  "#ff3a3a",
    ECUStatus.ERROR:    "#ff3a3a",
    ECUStatus.UNKNOWN:  "#5a7090",
}

class ECUListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        bus.scan_started.connect(self._on_scan_start)
        bus.scan_progress.connect(self._on_scan_progress)
        bus.scan_finished.connect(self._on_scan_finished)
        bus.connection_changed.connect(self._on_connection_changed)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        # Header row
        hdr = QHBoxLayout()
        lbl = QLabel("ECU LIST")
        lbl.setObjectName("label_section")
        hdr.addWidget(lbl)
        hdr.addStretch()
        self._btn_scan = QPushButton("SCAN")
        self._btn_scan.setObjectName("btn_primary")
        self._btn_scan.setFixedWidth(80)
        self._btn_scan.setEnabled(False)
        self._btn_scan.clicked.connect(self._on_scan_clicked)
        hdr.addWidget(self._btn_scan)
        root.addLayout(hdr)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setFixedHeight(4)
        self._progress.setTextVisible(False)
        self._progress.hide()
        root.addWidget(self._progress)

        # Tree
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["ADDRESS", "NAME", "STATUS", "DTCs", "SW"])
        self._tree.setColumnWidth(0, 80)
        self._tree.setColumnWidth(1, 140)
        self._tree.setColumnWidth(2, 80)
        self._tree.setColumnWidth(3, 50)
        self._tree.setAlternatingRowColors(True)
        self._tree.itemClicked.connect(self._on_item_clicked)
        root.addWidget(self._tree)

        # Footer count
        self._lbl_count = QLabel("0 ECU(s)")
        self._lbl_count.setObjectName("label_section")
        root.addWidget(self._lbl_count)

    @pyqtSlot()
    def _on_scan_clicked(self):
        bus.log_message.emit("INFO", "Scan requested (connect a UDS factory first)")
        # Actual scan is triggered by AppController; this just emits a request
        bus.status_message.emit("Scanning ECUs...")

    @pyqtSlot()
    def _on_scan_start(self):
        self._tree.clear()
        self._progress.setValue(0)
        self._progress.show()
        self._btn_scan.setEnabled(False)

    @pyqtSlot(int, int)
    def _on_scan_progress(self, current: int, total: int):
        self._progress.setMaximum(total)
        self._progress.setValue(current)

    @pyqtSlot(list)
    def _on_scan_finished(self, ecus: list):
        self._progress.hide()
        self._tree.clear()
        for ecu in ecus:
            self._add_ecu_item(ecu)
        self._lbl_count.setText(f"{len(ecus)} ECU(s) found")
        self._btn_scan.setEnabled(True)
        bus.status_message.emit(f"Scan complete — {len(ecus)} ECU(s)")

    def _add_ecu_item(self, ecu: ECU):
        item = QTreeWidgetItem([
            ecu.address_hex,
            ecu.name,
            ecu.status.value.upper(),
            str(ecu.dtc_count),
            ecu.sw_version or "—",
        ])
        color = STATUS_COLORS.get(ecu.status, "#5a7090")
        item.setForeground(2, QColor(color))
        item.setData(0, Qt.ItemDataRole.UserRole, ecu)
        self._tree.addTopLevelItem(item)

    @pyqtSlot(QTreeWidgetItem, int)
    def _on_item_clicked(self, item: QTreeWidgetItem, _col: int):
        ecu = item.data(0, Qt.ItemDataRole.UserRole)
        if ecu:
            bus.ecu_selected.emit(ecu)
            bus.status_message.emit(f"Selected: {ecu.name} ({ecu.address_hex})")

    @pyqtSlot(bool, str)
    def _on_connection_changed(self, connected: bool, _desc: str):
        self._btn_scan.setEnabled(connected)
        if not connected:
            self._tree.clear()
            self._lbl_count.setText("0 ECU(s)")
