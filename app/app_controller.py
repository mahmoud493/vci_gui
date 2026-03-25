"""app/app_controller.py — Wires together core services and UI events."""
#from typing import Optional
from core.diagnostic_engine import DiagnosticEngine
from core.ecu_manager       import ECUManager
from app.event_bus          import bus
from app.state_manager      import state
from services.scan_service  import ScanService
from utils.logger           import log

class AppController:
    """
    Central controller.
    Connects EventBus signals to core logic.
    Created once in main.py after QApplication is constructed.
    """

    def __init__(self):
        self._ecu_mgr  = ECUManager()
        self._diag_eng = DiagnosticEngine(self._ecu_mgr)
        self._scan_svc = ScanService()
        self._connect_signals()
        log.info("AppController initialized")

    def _connect_signals(self):
        bus.connection_changed.connect(self._on_connection_changed)
        bus.ecu_selected.connect(self._on_ecu_selected)
        bus.dtc_list_updated.connect(self._on_dtcs_received)

    def _on_connection_changed(self, connected: bool, desc: str):
        if connected:
            log.info(f"Transport connected: {desc}")
            bus.status_message.emit(f"Connected: {desc}")
        else:
            log.info("Transport disconnected")
            self._ecu_mgr.close_session()
            state.reset()
            bus.status_message.emit("Disconnected")

    def _on_ecu_selected(self, ecu):
        if ecu is None:
            return
        state.selected_ecu = ecu
        log.info(f"ECU selected: {ecu.address_hex}")

    def _on_dtcs_received(self, dtcs: list):
        state.dtc_list = dtcs
        log.info(f"{len(dtcs)} DTC(s) in state")
