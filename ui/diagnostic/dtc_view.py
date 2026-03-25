"""ui/diagnostic/dtc_view.py — DTC read/clear panel."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor
from models.dtc import DTC, DTCStatus
from app.event_bus import bus

STATUS_COLORS = {
    DTCStatus.ACTIVE:    "#ff3a3a",
    DTCStatus.PENDING:   "#ffb300",
    DTCStatus.PERMANENT: "#ff6600",
    DTCStatus.STORED:    "#5af078",
}

class DTCView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        bus.dtc_list_updated.connect(self._on_dtc_list)
        bus.connection_changed.connect(self._on_connection_changed)
        bus.dtcs_cleared.connect(self._on_dtcs_cleared)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(6)

        # Toolbar
        toolbar = QHBoxLayout()

        lbl = QLabel("FAULT CODES")
        lbl.setObjectName("label_section")
        toolbar.addWidget(lbl)
        toolbar.addStretch()

        lbl_mask = QLabel("Filter:")
        toolbar.addWidget(lbl_mask)
        self._cbo_filter = QComboBox()
        self._cbo_filter.addItems(["All", "Active", "Pending", "Stored", "Permanent"])
        self._cbo_filter.setFixedWidth(100)
        self._cbo_filter.currentTextChanged.connect(self._apply_filter)
        toolbar.addWidget(self._cbo_filter)

        self._btn_read = QPushButton("READ DTCs")
        self._btn_read.setObjectName("btn_primary")
        self._btn_read.setEnabled(False)
        self._btn_read.clicked.connect(self._on_read)
        toolbar.addWidget(self._btn_read)

        self._btn_clear = QPushButton("CLEAR ALL")
        self._btn_clear.setObjectName("btn_danger")
        self._btn_clear.setEnabled(False)
        self._btn_clear.clicked.connect(self._on_clear)
        toolbar.addWidget(self._btn_clear)

        root.addLayout(toolbar)

        # DTC table
        self._table = QTableWidget(0, 5)
        self._table.setHorizontalHeaderLabels(["CODE", "STATUS", "SEVERITY", "CONFIRMED", "DESCRIPTION"])
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(0, 80)
        self._table.setColumnWidth(1, 90)
        self._table.setColumnWidth(2, 90)
        self._table.setColumnWidth(3, 80)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

        # Footer
        foot = QHBoxLayout()
        self._lbl_count = QLabel("0 fault code(s)")
        self._lbl_count.setObjectName("label_section")
        foot.addWidget(self._lbl_count)
        root.addLayout(foot)

        self._all_dtcs: list = []

    @pyqtSlot(list)
    def _on_dtc_list(self, dtcs: list):
        self._all_dtcs = dtcs
        self._populate(dtcs)
        self._btn_clear.setEnabled(len(dtcs) > 0)

    def _populate(self, dtcs: list):
        self._table.setRowCount(0)
        for dtc in dtcs:
            row = self._table.rowCount()
            self._table.insertRow(row)
            code_item = QTableWidgetItem(dtc.code_str)
            code_item.setForeground(QColor("#00d4ff"))
            self._table.setItem(row, 0, code_item)

            st = dtc.status
            st_item = QTableWidgetItem(st.value.upper())
            st_item.setForeground(QColor(STATUS_COLORS.get(st, "#c8d0dc")))
            self._table.setItem(row, 1, st_item)

            self._table.setItem(row, 2, QTableWidgetItem(dtc.severity.name))
            conf_item = QTableWidgetItem("YES" if dtc.confirmed else "NO")
            conf_item.setForeground(QColor("#ff3a3a" if dtc.confirmed else "#5a7090"))
            self._table.setItem(row, 3, conf_item)
            self._table.setItem(row, 4, QTableWidgetItem(dtc.description or "—"))

        self._lbl_count.setText(f"{len(dtcs)} fault code(s)")

    def _apply_filter(self, text: str):
        if text == "All" or not self._all_dtcs:
            self._populate(self._all_dtcs)
            return
        status_map = {
            "Active": DTCStatus.ACTIVE, "Pending": DTCStatus.PENDING,
            "Stored": DTCStatus.STORED, "Permanent": DTCStatus.PERMANENT,
        }
        target = status_map.get(text)
        self._populate([d for d in self._all_dtcs if d.status == target])

    @pyqtSlot()
    def _on_read(self):
        bus.log_message.emit("INFO", "Reading DTCs...")
        bus.status_message.emit("Reading DTCs...")
        # AppController handles the actual UDS call

    @pyqtSlot()
    def _on_clear(self):
        reply = QMessageBox.question(
            self, "Confirm Clear",
            "Clear ALL stored DTCs from the ECU?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            bus.log_message.emit("WARN", "Clearing DTCs...")
            bus.status_message.emit("Clearing DTCs...")

    @pyqtSlot(int)
    def _on_dtcs_cleared(self, _addr: int):
        self._all_dtcs = []
        self._table.setRowCount(0)
        self._lbl_count.setText("0 fault code(s)")
        self._btn_clear.setEnabled(False)

    @pyqtSlot(bool, str)
    def _on_connection_changed(self, connected: bool, _desc: str):
        self._btn_read.setEnabled(connected)
        if not connected:
            self._all_dtcs = []
            self._table.setRowCount(0)
            self._lbl_count.setText("0 fault code(s)")
