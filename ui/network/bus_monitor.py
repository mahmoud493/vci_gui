"""ui/network/bus_monitor.py — Bus statistics + frame viewer container."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QFormLayout, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from ui.network.frame_viewer import FrameViewer
from app.event_bus import bus

class BusMonitor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rx_count = 0
        self._tx_count = 0
        self._setup_ui()
        bus.frame_received.connect(self._on_rx)
        bus.frame_tx.connect(self._on_tx)
        self._stats_timer = QTimer(self)
        self._stats_timer.timeout.connect(self._update_stats)
        self._stats_timer.start(500)

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # ── Stats panel ────────────────────────────────────────────
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        rx_grp = QGroupBox("RX FRAMES")
        rx_form = QFormLayout(rx_grp)
        self._lbl_rx_total = QLabel("0")
        self._lbl_rx_total.setObjectName("label_value")
        self._lbl_rx_rate  = QLabel("0 / s")
        rx_form.addRow("Total:", self._lbl_rx_total)
        rx_form.addRow("Rate:",  self._lbl_rx_rate)
        stats_layout.addWidget(rx_grp)

        tx_grp = QGroupBox("TX FRAMES")
        tx_form = QFormLayout(tx_grp)
        self._lbl_tx_total = QLabel("0")
        self._lbl_tx_total.setObjectName("label_value")
        self._lbl_tx_rate  = QLabel("0 / s")
        tx_form.addRow("Total:", self._lbl_tx_total)
        tx_form.addRow("Rate:",  self._lbl_tx_rate)
        stats_layout.addWidget(tx_grp)

        err_grp = QGroupBox("BUS ERRORS")
        err_form = QFormLayout(err_grp)
        self._lbl_errors = QLabel("0")
        self._lbl_errors.setObjectName("label_warn")
        err_form.addRow("Count:", self._lbl_errors)
        stats_layout.addWidget(err_grp)

        btn_reset = QPushButton("RESET COUNTERS")
        btn_reset.clicked.connect(self._reset_stats)
        stats_layout.addWidget(btn_reset)
        stats_layout.addStretch()

        splitter.addWidget(stats_widget)

        # ── Frame viewer ───────────────────────────────────────────
        self._frame_viewer = FrameViewer()
        splitter.addWidget(self._frame_viewer)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

        self._prev_rx = 0
        self._prev_tx = 0

    @pyqtSlot(object)
    def _on_rx(self, _): self._rx_count += 1

    @pyqtSlot(object)
    def _on_tx(self, _): self._tx_count += 1

    def _update_stats(self):
        self._lbl_rx_total.setText(str(self._rx_count))
        self._lbl_tx_total.setText(str(self._tx_count))
        rx_rate = (self._rx_count - self._prev_rx) * 2
        tx_rate = (self._tx_count - self._prev_tx) * 2
        self._lbl_rx_rate.setText(f"{rx_rate} / s")
        self._lbl_tx_rate.setText(f"{tx_rate} / s")
        self._prev_rx = self._rx_count
        self._prev_tx = self._tx_count

    def _reset_stats(self):
        self._rx_count = self._tx_count = self._prev_rx = self._prev_tx = 0
        self._lbl_errors.setText("0")
