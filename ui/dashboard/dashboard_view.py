"""ui/dashboard/dashboard_view.py — Main dashboard tab."""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QGroupBox, QLabel, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from ui.dashboard.ecu_list_widget import ECUListWidget
from app.event_bus import bus

class DashboardView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        bus.ecu_selected.connect(self._on_ecu_selected)
        bus.vehicle_updated.connect(self._on_vehicle_updated)

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ── Left: ECU list ─────────────────────────────────────────
        self._ecu_list = ECUListWidget()
        splitter.addWidget(self._ecu_list)

        # ── Right: Vehicle info + selected ECU detail ──────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(4, 0, 0, 0)

        # Vehicle info group
        veh_grp = QGroupBox("VEHICLE INFO")
        veh_form = QFormLayout(veh_grp)
        self._lbl_vin   = QLabel("—")
        self._lbl_proto = QLabel("—")
        self._lbl_speed = QLabel("—")
        self._lbl_dtc   = QLabel("—")
        veh_form.addRow("VIN:",          self._lbl_vin)
        veh_form.addRow("Protocol:",     self._lbl_proto)
        veh_form.addRow("Bus Speed:",    self._lbl_speed)
        veh_form.addRow("Total DTCs:",   self._lbl_dtc)
        right_layout.addWidget(veh_grp)

        # Selected ECU detail group
        ecu_grp = QGroupBox("SELECTED ECU")
        ecu_form = QFormLayout(ecu_grp)
        self._lbl_ecu_addr  = QLabel("—")
        self._lbl_ecu_name  = QLabel("—")
        self._lbl_ecu_sw    = QLabel("—")
        self._lbl_ecu_hw    = QLabel("—")
        self._lbl_ecu_sess  = QLabel("—")
        ecu_form.addRow("Address:",  self._lbl_ecu_addr)
        ecu_form.addRow("Name:",     self._lbl_ecu_name)
        ecu_form.addRow("SW:",       self._lbl_ecu_sw)
        ecu_form.addRow("HW:",       self._lbl_ecu_hw)
        ecu_form.addRow("Session:",  self._lbl_ecu_sess)
        right_layout.addWidget(ecu_grp)
        right_layout.addStretch()

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter)

    @pyqtSlot(object)
    def _on_ecu_selected(self, ecu):
        if ecu:
            self._lbl_ecu_addr.setText(ecu.address_hex)
            self._lbl_ecu_name.setText(ecu.name)
            self._lbl_ecu_sw.setText(ecu.sw_version or "—")
            self._lbl_ecu_hw.setText(ecu.hw_version or "—")
            self._lbl_ecu_sess.setText("ACTIVE" if ecu.session_active else "DEFAULT")

    @pyqtSlot(object)
    def _on_vehicle_updated(self, vehicle):
        from utils.converters import baud_to_str
        self._lbl_vin.setText(vehicle.vin_display)
        self._lbl_proto.setText(vehicle.protocol or "—")
        self._lbl_speed.setText(baud_to_str(vehicle.bus_speed) if vehicle.bus_speed else "—")
        self._lbl_dtc.setText(str(vehicle.total_dtc_count))
