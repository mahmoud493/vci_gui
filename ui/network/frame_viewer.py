"""ui/network/frame_viewer.py — Raw CAN frame viewer (hex dump table)."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from PyQt6.QtGui import QColor
from models.message import CANMessage
from app.event_bus import bus
from utils.constants import FRAME_TABLE_MAX

class FrameViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer: list = []
        self._paused = False
        self._filter_str = ""
        self._setup_ui()
        bus.frame_received.connect(self._on_frame)
        bus.frame_tx.connect(self._on_frame_tx)

        # Batch-update timer (every 250 ms) to avoid GUI flood
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._flush_buffer)
        self._update_timer.start(250)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        # Toolbar
        toolbar = QHBoxLayout()
        lbl = QLabel("FRAME DUMP")
        lbl.setObjectName("label_section")
        toolbar.addWidget(lbl)

        lbl_filter = QLabel("ID Filter:")
        toolbar.addWidget(lbl_filter)
        self._filter_edit = QLineEdit()
        self._filter_edit.setPlaceholderText("e.g. 7E0 or 18DA")
        self._filter_edit.setFixedWidth(140)
        self._filter_edit.textChanged.connect(self._on_filter_changed)
        toolbar.addWidget(self._filter_edit)

        toolbar.addStretch()

        self._btn_pause = QPushButton("PAUSE")
        self._btn_pause.setFixedWidth(70)
        self._btn_pause.clicked.connect(self._toggle_pause)
        toolbar.addWidget(self._btn_pause)

        btn_clear = QPushButton("CLEAR")
        btn_clear.setFixedWidth(70)
        btn_clear.clicked.connect(self._table.clearContents if hasattr(self, '_table') else lambda: None)
        btn_clear.clicked.connect(self._clear)
        toolbar.addWidget(btn_clear)

        root.addLayout(toolbar)

        # Table
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(["TIME (ms)", "CH", "DIR", "ARB ID", "DLC", "DATA"])
        self._table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(0, 90)
        self._table.setColumnWidth(1, 50)
        self._table.setColumnWidth(2, 40)
        self._table.setColumnWidth(3, 80)
        self._table.setColumnWidth(4, 40)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        root.addWidget(self._table)

        # Footer
        foot = QHBoxLayout()
        self._lbl_count = QLabel("0 frames")
        self._lbl_count.setObjectName("label_section")
        foot.addWidget(self._lbl_count)
        root.addLayout(foot)

    @pyqtSlot(object)
    def _on_frame(self, msg: CANMessage):
        if not self._paused:
            self._buffer.append((msg, False))

    @pyqtSlot(object)
    def _on_frame_tx(self, msg: CANMessage):
        if not self._paused:
            self._buffer.append((msg, True))

    def _flush_buffer(self):
        if not self._buffer:
            return
        batch, self._buffer = self._buffer[:200], self._buffer[200:]
        for msg, is_tx in batch:
            if self._filter_str and self._filter_str.upper() not in msg.arb_id_hex.upper():
                continue
            self._add_row(msg, is_tx)
        # Trim table
        while self._table.rowCount() > FRAME_TABLE_MAX:
            self._table.removeRow(0)
        self._lbl_count.setText(f"{self._table.rowCount()} frames")

    def _add_row(self, msg: CANMessage, is_tx: bool):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setRowHeight(row, 18)

        dir_color = "#00d4ff" if is_tx else "#5af078"
        dir_str   = "TX" if is_tx else "RX"

        items = [
            (msg.timestamp_ms, "#5a7090"),
            (msg.channel,      "#5a7090"),
            (dir_str,          dir_color),
            (msg.arb_id_hex,   "#00d4ff"),
            (str(msg.dlc),     "#5a7090"),
            (msg.data_hex,     "#c8d0dc"),
        ]
        for col, (text, color) in enumerate(items):
            item = QTableWidgetItem(text)
            item.setForeground(QColor(color))
            self._table.setItem(row, col, item)

        if row % 2 == 0:
            for col in range(6):
                if self._table.item(row, col):
                    self._table.item(row, col).setBackground(QColor("#0e1520"))

    def _on_filter_changed(self, text: str):
        self._filter_str = text.strip()

    def _toggle_pause(self):
        self._paused = not self._paused
        self._btn_pause.setText("RESUME" if self._paused else "PAUSE")

    def _clear(self):
        self._table.setRowCount(0)
        self._buffer.clear()
        self._lbl_count.setText("0 frames")
