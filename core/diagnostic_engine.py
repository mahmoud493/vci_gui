"""core/diagnostic_engine.py — High-level diagnostic orchestration."""
import threading
from typing import Optional, List, Callable
from models.ecu import ECU, ECUStatus
from models.dtc import DTC
from models.vehicle import Vehicle
from core.ecu_manager import ECUManager
from core.vehicle_model import STANDARD_LIVE_DATA
from communication.protocol.uds_client import UDSClient, UDSError
from app.event_bus import bus
from utils.constants import *
from utils.converters import bytes_to_uint, scale_value
from utils.logger import log

class DiagnosticEngine:
    def __init__(self, ecu_mgr: ECUManager):
        self._mgr       = ecu_mgr
        self._live_thread: Optional[threading.Thread] = None
        self._live_run  = False
        self._live_dids: List[str] = []

    # ── Scan ──────────────────────────────────────────────────────────────
    def scan_ecus(self, uds_factory: Callable[[int], UDSClient],
                  addr_range: List[int] = None) -> List[ECU]:
        if addr_range is None:
            addr_range = UDS_ADDR_RANGE_STD
        found: List[ECU] = []
        bus.scan_started.emit()
        total = len(addr_range)
        for i, addr in enumerate(addr_range):
            bus.scan_progress.emit(i, total)
            try:
                uds = uds_factory(addr)
                uds.diagnostic_session_control(SESSION_DEFAULT)
                ecu = ECU(address=addr, status=ECUStatus.PRESENT)
                # Try to get SW version
                try:
                    sw = uds.read_data_by_id(DID_SW_VERSION)
                    ecu.sw_version = sw.decode("ascii", errors="replace").strip()
                except Exception:
                    pass
                found.append(ecu)
                log.info(f"ECU found at 0x{addr:03X}")
                bus.log_message.emit("INFO", f"ECU found: 0x{addr:03X}")
            except (TimeoutError, IOError):
                pass
            except Exception as e:
                log.debug(f"0x{addr:03X}: {e}")
        bus.scan_finished.emit(found)
        return found

    # ── Live data ─────────────────────────────────────────────────────────
    def start_live_data(self, did_keys: List[str]):
        if self._live_run:
            return
        self._live_dids = did_keys
        self._live_run  = True
        self._live_thread = threading.Thread(
            target=self._live_loop, daemon=True, name="LiveData"
        )
        self._live_thread.start()

    def stop_live_data(self):
        self._live_run = False
        if self._live_thread:
            self._live_thread.join(timeout=2.0)

    def _live_loop(self):
        import time
        uds = self._mgr._uds
        if not uds:
            return
        while self._live_run:
            values = {}
            for key in self._live_dids:
                defn = STANDARD_LIVE_DATA.get(key)
                if not defn:
                    continue
                try:
                    raw  = uds.read_data_by_id(defn.did)
                    uint = bytes_to_uint(raw[:defn.byte_len])
                    val  = scale_value(uint, defn.factor, defn.offset)
                    values[key] = round(val, 3)
                except Exception:
                    pass
            if values:
                bus.live_data_updated.emit(values)
            time.sleep(LIVE_DATA_UPDATE_MS / 1000)
