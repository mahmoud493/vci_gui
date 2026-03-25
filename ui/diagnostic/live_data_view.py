"""ui/diagnostic/live_data_view.py — Real-time live data with mini bar graphs."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QCheckBox, QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QColor
from core.vehicle_model import STANDARD_LIVE_DATA
from app.event_bus import bus

class LiveDataView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._active_keys: list = []
        self._setup_ui()
        bus.live_data_updated.connect(self._on_live_data)
        bus.connection_changed.connect(self._on_connection_changed)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)

        # Toolbar
        toolbar = QHBoxLayout()
        lbl = QLabel("LIVE DATA")
        lbl.setObjectName("label_section")
        toolbar.addWidget(lbl)
        toolbar.addStretch()
        self._btn_start = QPushButton("START")
        self._btn_start.setObjectName("btn_success")
        self._btn_start.setEnabled(False)
        self._btn_start.clicked.connect(self._on_toggle_live)
        toolbar.addWidget(self._btn_start)
        root.addLayout(toolbar)

        # Parameter selection (checkboxes)
        sel_widget = QWidget()
        sel_layout = QHBoxLayout(sel_widget)
        sel_layout.setContentsMargins(0, 0, 0, 0)
        self._checkboxes: dict = {}
        for key, defn in STANDARD_LIVE_DATA.items():
            cb = QCheckBox(defn.name)
            cb.setChecked(True)
            self._checkboxes[key] = cb
            sel_layout.addWidget(cb)
        sel_layout.addStretch()
        root.addWidget(sel_widget)

        # Live data table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["PARAMETER", "VALUE", "UNIT", "RANGE"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(1, 100)
        self._table.setColumnWidth(2, 60)
        self._table.setColumnWidth(3, 120)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table)

        # Pre-populate rows
        self._row_map: dict = {}
        for key, defn in STANDARD_LIVE_DATA.items():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(defn.name))
            val_item = QTableWidgetItem("—")
            val_item.setForeground(QColor("#00d4ff"))
            val_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._table.setItem(row, 1, val_item)
            self._table.setItem(row, 2, QTableWidgetItem(defn.unit))
            bar = QProgressBar()
            bar.setRange(int(defn.min_val), int(defn.max_val))
            bar.setValue(int(defn.min_val))
            bar.setTextVisible(False)
            bar.setFixedHeight(10)
            self._table.setCellWidget(row, 3, bar)
            self._row_map[key] = (row, bar)

        self._running = False

    @pyqtSlot(dict)
    def _on_live_data(self, data: dict):
        for key, value in data.items():
            entry = self._row_map.get(key)
            if not entry:
                continue
            row, bar = entry
            defn = STANDARD_LIVE_DATA[key]
            val_str = f"{value:.2f}"
            val_item = self._table.item(row, 1)
            if val_item:
                val_item.setText(val_str)
            bar.setValue(int(max(defn.min_val, min(defn.max_val, value))))

    @pyqtSlot()
    def _on_toggle_live(self):
        if self._running:
            self._running = False
            self._btn_start.setText("START")
            self._btn_start.setObjectName("btn_success")
            bus.log_message.emit("INFO", "Live data stopped")
        else:
            self._active_keys = [k for k, cb in self._checkboxes.items() if cb.isChecked()]
            if not self._active_keys:
                bus.log_message.emit("WARN", "No parameters selected")
                return
            self._running = True
            self._btn_start.setText("STOP")
            self._btn_start.setObjectName("btn_danger")
            bus.log_message.emit("INFO", f"Live data started: {len(self._active_keys)} params")
        self._btn_start.style().unpolish(self._btn_start)
        self._btn_start.style().polish(self._btn_start)

    @pyqtSlot(bool, str)
    def _on_connection_changed(self, connected: bool, _desc: str):
        self._btn_start.setEnabled(connected)
        if not connected and self._running:
            self._running = False
            self._btn_start.setText("START")
