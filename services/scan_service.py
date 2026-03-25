"""services/scan_service.py — Background ECU scan service."""
import threading
from typing import List, Optional, Callable
from models.ecu import ECU, ECUStatus
from app.event_bus import bus
from utils.constants import UDS_ADDR_RANGE_STD
from utils.logger import log

class ScanService:
    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start_scan(self, uds_factory: Callable, addr_range: List[int] = None):
        if self._running:
            log.warning("Scan already in progress")
            return
        if addr_range is None:
            addr_range = UDS_ADDR_RANGE_STD
        self._running = True
        self._thread  = threading.Thread(
            target=self._scan_worker,
            args=(uds_factory, addr_range),
            daemon=True, name="ScanService"
        )
        self._thread.start()

    def stop_scan(self):
        self._running = False

    def _scan_worker(self, uds_factory, addr_range):
        found: List[ECU] = []
        total = len(addr_range)
        bus.scan_started.emit()
        bus.log_message.emit("INFO", f"Scanning {total} addresses...")
        for i, addr in enumerate(addr_range):
            if not self._running:
                break
            bus.scan_progress.emit(i + 1, total)
            try:
                uds = uds_factory(addr)
                uds.diagnostic_session_control(0x01)
                ecu = ECU(address=addr, status=ECUStatus.PRESENT,
                          name=f"ECU @ 0x{addr:03X}")
                found.append(ecu)
                bus.log_message.emit("INFO", f"  → Found ECU at 0x{addr:03X}")
            except (TimeoutError, IOError):
                pass
            except Exception as e:
                log.debug(f"0x{addr:03X}: {e}")
        self._running = False
        bus.scan_finished.emit(found)
        bus.log_message.emit("INFO", f"Scan complete. {len(found)} ECU(s) found.")
