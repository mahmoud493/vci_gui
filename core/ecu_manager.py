"""core/ecu_manager.py — ECU management and UDS session handling."""
import threading
from typing import Optional, List
from models.ecu import ECU, ECUStatus
from models.vehicle import Vehicle
from models.dtc import DTC
from communication.protocol.uds_client import UDSClient, UDSError
from communication.protocol.isotp_stack import ISOTPStack
from core.dtc_parser import DTCParser
from utils.constants import *
from utils.logger import log

class ECUManager:
    def __init__(self):
        self._vehicle   = Vehicle()
        self._uds:      Optional[UDSClient] = None
        self._tp_timer: Optional[threading.Timer] = None

    def set_uds_client(self, uds: UDSClient):
        self._uds = uds

    def get_vehicle(self) -> Vehicle:
        return self._vehicle

    # ── VIN ───────────────────────────────────────────────────────────────
    def read_vin(self) -> str:
        if not self._uds:
            return ""
        try:
            data = self._uds.read_data_by_id(DID_VIN)
            vin  = data.decode("ascii", errors="replace").strip()
            self._vehicle.vin = vin
            log.info(f"VIN: {vin}")
            return vin
        except (UDSError, TimeoutError) as e:
            log.warning(f"VIN read failed: {e}")
            return ""

    # ── Session ───────────────────────────────────────────────────────────
    def open_extended_session(self) -> bool:
        if not self._uds:
            return False
        try:
            self._uds.diagnostic_session_control(SESSION_EXTENDED)
            self._start_tester_present()
            log.info("Extended diagnostic session opened")
            return True
        except Exception as e:
            log.error(f"Session open failed: {e}")
            return False

    def close_session(self):
        self._stop_tester_present()
        if self._uds:
            try:
                self._uds.diagnostic_session_control(SESSION_DEFAULT)
            except Exception:
                pass
        log.info("Session closed")

    def _start_tester_present(self):
        """Send TesterPresent every 2 s to keep session alive."""
        def _tp():
            if self._uds:
                try:
                    self._uds.tester_present(suppress=True)
                except Exception:
                    pass
            self._tp_timer = threading.Timer(2.0, _tp)
            self._tp_timer.daemon = True
            self._tp_timer.start()
        _tp()

    def _stop_tester_present(self):
        if self._tp_timer:
            self._tp_timer.cancel()
            self._tp_timer = None

    # ── ECU info ──────────────────────────────────────────────────────────
    def read_ecu_info(self, ecu: ECU) -> bool:
        if not self._uds:
            return False
        try:
            sw = self._uds.read_data_by_id(DID_SW_VERSION)
            ecu.sw_version = sw.decode("ascii", errors="replace").strip()
        except Exception:
            pass
        try:
            hw = self._uds.read_data_by_id(DID_HW_VERSION)
            ecu.hw_version = hw.decode("ascii", errors="replace").strip()
        except Exception:
            pass
        return True

    # ── DTCs ──────────────────────────────────────────────────────────────
    def read_dtcs(self, status_mask: int = 0xFF) -> List[DTC]:
        if not self._uds:
            return []
        try:
            raw = self._uds.read_dtc_by_status_mask(status_mask)
            dtcs = DTCParser.parse_read_dtc_response(raw)
            for dtc in dtcs:
                dtc.description = DTCParser.lookup_description(dtc.code_str)
            return dtcs
        except Exception as e:
            log.error(f"ReadDTC failed: {e}")
            return []

    def clear_dtcs(self) -> bool:
        if not self._uds:
            return False
        try:
            self._uds.clear_dtc()
            log.info("DTCs cleared")
            return True
        except Exception as e:
            log.error(f"ClearDTC failed: {e}")
            return False
