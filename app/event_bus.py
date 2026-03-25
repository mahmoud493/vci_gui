"""app/event_bus.py — Application-wide Qt signal bus (singleton)."""
from PyQt6.QtCore import QObject, pyqtSignal
from models.ecu import ECU
from models.dtc import DTC
from models.message import CANMessage

class EventBus(QObject):
    """Central signal dispatcher. Import the global `bus` instance."""

    # ── Connection ───────────────────────────────────
    connection_changed   = pyqtSignal(bool, str)   # (connected, transport_desc)
    transport_error      = pyqtSignal(str)

    # ── Scan / ECU ───────────────────────────────────
    scan_started         = pyqtSignal()
    scan_progress        = pyqtSignal(int, int)    # (current, total)
    scan_finished        = pyqtSignal(list)        # list[ECU]
    ecu_selected         = pyqtSignal(object)      # ECU | None

    # ── DTC ──────────────────────────────────────────
    dtc_list_updated     = pyqtSignal(list)        # list[DTC]
    dtcs_cleared         = pyqtSignal(int)         # ecu_address

    # ── Live data ────────────────────────────────────
    live_data_updated    = pyqtSignal(dict)        # {did_str: value}

    # ── CAN frames ───────────────────────────────────
    frame_received       = pyqtSignal(object)      # CANMessage
    frame_tx             = pyqtSignal(object)      # CANMessage

    # ── Log ──────────────────────────────────────────
    log_message          = pyqtSignal(str, str)    # (level, text)

    # ── Vehicle ──────────────────────────────────────
    vehicle_updated      = pyqtSignal(object)      # Vehicle

    # ── Status ───────────────────────────────────────
    status_message       = pyqtSignal(str)

# Global singleton
bus = EventBus()
