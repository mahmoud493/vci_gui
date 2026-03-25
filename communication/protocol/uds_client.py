"""communication/protocol/uds_client.py — UDS (ISO 14229) client."""
import threading
import time
from typing import Optional, Tuple
from .isotp_stack import ISOTPStack
from utils.constants import *
from utils.logger import log

class UDSError(Exception):
    def __init__(self, nrc: int):
        self.nrc = nrc
        super().__init__(f"NRC 0x{nrc:02X}: {NRC.get(nrc, 'unknown')}")

class UDSClient:
    def __init__(self, isotp: ISOTPStack, timeout_ms: int = T_REQUEST_MS):
        self._isotp   = isotp
        self._timeout = timeout_ms / 1000.0
        self._resp:   Optional[bytes] = None
        self._event   = threading.Event()
        self._lock    = threading.Lock()
        self._isotp.set_response_callback(self._on_response)

    # ── Internal ──────────────────────────────────────────────────────────
    def _on_response(self, data: bytes):
        with self._lock:
            self._resp = data
        self._event.set()

    def _request(self, payload: bytes) -> bytes:
        with self._lock:
            self._resp = None
            self._event.clear()
        if not self._isotp.send(payload):
            raise IOError("ISO-TP send failed")
        if not self._event.wait(self._timeout):
            raise TimeoutError(f"No UDS response (timeout {self._timeout*1000:.0f} ms)")
        data = self._resp
        if data[0] == 0x7F:
            nrc = data[2] if len(data) >= 3 else 0xFF
            if nrc == 0x78:                 # RCRRP — wait and retry
                self._event.clear()
                if not self._event.wait(T_P2_EXT_MS / 1000):
                    raise TimeoutError("RCRRP timeout")
                data = self._resp
                if data and data[0] == 0x7F:
                    raise UDSError(data[2])
            else:
                raise UDSError(nrc)
        return data

    # ── Public services ───────────────────────────────────────────────────
    def diagnostic_session_control(self, session: int = SESSION_DEFAULT) -> bytes:
        return self._request(bytes([SID_DIAGNOSTIC_SESSION_CONTROL, session]))

    def ecu_reset(self, reset_type: int = 0x01) -> bytes:
        return self._request(bytes([SID_ECU_RESET, reset_type]))

    def tester_present(self, suppress: bool = True) -> Optional[bytes]:
        sub = 0x80 if suppress else 0x00
        payload = bytes([SID_TESTER_PRESENT, sub])
        if suppress:
            self._isotp.send(payload)
            return None
        return self._request(payload)

    def security_access(self, level: int) -> Tuple[bytes, bytes]:
        """Returns (seed, key_placeholder). Key computation is application-specific."""
        resp = self._request(bytes([SID_SECURITY_ACCESS, level]))
        seed = resp[2:]
        log.debug(f"SecurityAccess seed: {seed.hex()}")
        return seed, b""

    def read_data_by_id(self, did: int) -> bytes:
        payload = bytes([SID_READ_DATA_BY_ID, (did >> 8) & 0xFF, did & 0xFF])
        resp    = self._request(payload)
        return resp[3:]  # Skip SID + DID echo

    def read_dtc_by_status_mask(self, status_mask: int = 0xFF) -> bytes:
        payload = bytes([SID_READ_DTC, 0x02, status_mask])
        return self._request(payload)

    def clear_dtc(self, group: int = 0xFFFFFF) -> bytes:
        g = group.to_bytes(3, "big")
        return self._request(bytes([0x14]) + g)

    def io_control(self, did: int, control_option: int, control_enable_mask: bytes = b"") -> bytes:
        payload = bytes([SID_IO_CONTROL, (did >> 8) & 0xFF, did & 0xFF, control_option])
        payload += control_enable_mask
        return self._request(payload)

    def routine_control(self, rtype: int, routine_id: int, data: bytes = b"") -> bytes:
        payload = bytes([SID_ROUTINE_CONTROL, rtype,
                         (routine_id >> 8) & 0xFF, routine_id & 0xFF]) + data
        return self._request(payload)
