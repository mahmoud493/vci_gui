"""communication/protocol/isotp_stack.py — ISO-TP (ISO 15765-2) framing layer."""
import threading
import time
from typing import Optional, Callable
from .can_interface import CANInterface
from models.message import CANMessage
from utils.logger import log

class ISOTPStack:
    """Minimal ISO-TP stack (single-frame + multi-frame TX/RX)."""

    SF_MAX_PAYLOAD  = 7    # Single Frame max payload (classic CAN)
    FF_PAYLOAD_BYTE = 6    # First Frame payload start
    CF_PAYLOAD_BYTE = 7    # Consecutive Frame max payload

    def __init__(self, can: CANInterface, tx_id: int, rx_id: int):
        self._can    = can
        self._tx_id  = tx_id
        self._rx_id  = rx_id
        self._rx_buf = bytearray()
        self._rx_len = 0
        self._sn     = 0
        self._rx_cb: Optional[Callable[[bytes], None]] = None
        self._lock   = threading.Lock()

    def set_response_callback(self, cb: Callable[[bytes], None]):
        self._rx_cb = cb

    def send(self, data: bytes) -> bool:
        if len(data) <= self.SF_MAX_PAYLOAD:
            return self._send_sf(data)
        return self._send_mf(data)

    def _send_sf(self, data: bytes) -> bool:
        frame = bytes([len(data)]) + data + bytes(7 - len(data))
        msg = CANMessage(arb_id=self._tx_id, data=frame, is_rx=False)
        return self._can.send(msg)

    def _send_mf(self, data: bytes) -> bool:
        # First Frame
        length = len(data)
        ff_payload = data[:self.FF_PAYLOAD_BYTE]
        ff = bytes([0x10 | (length >> 8), length & 0xFF]) + ff_payload
        msg = CANMessage(arb_id=self._tx_id, data=ff, is_rx=False)
        if not self._can.send(msg):
            return False
        # Consecutive Frames
        sn = 1
        offset = self.FF_PAYLOAD_BYTE
        while offset < len(data):
            chunk = data[offset:offset + self.CF_PAYLOAD_BYTE]
            cf = bytes([0x20 | (sn & 0x0F)]) + chunk + bytes(self.CF_PAYLOAD_BYTE - len(chunk))
            cf_msg = CANMessage(arb_id=self._tx_id, data=cf, is_rx=False)
            self._can.send(cf_msg)
            sn += 1
            offset += self.CF_PAYLOAD_BYTE
            time.sleep(0.001)  # ST_min placeholder
        return True

    def on_can_frame(self, msg: CANMessage):
        if msg.arb_id != self._rx_id:
            return
        data = msg.data
        pci  = data[0] & 0xF0

        if pci == 0x00:    # Single Frame
            length = data[0] & 0x0F
            self._dispatch(bytes(data[1:1 + length]))

        elif pci == 0x10:  # First Frame
            self._rx_len = ((data[0] & 0x0F) << 8) | data[1]
            self._rx_buf = bytearray(data[2:8])
            self._sn     = 1
            self._send_fc()

        elif pci == 0x20:  # Consecutive Frame
            sn = data[0] & 0x0F
            if sn == (self._sn & 0x0F):
                self._rx_buf += data[1:8]
                self._sn += 1
                if len(self._rx_buf) >= self._rx_len:
                    self._dispatch(bytes(self._rx_buf[:self._rx_len]))

        elif pci == 0x30:  # Flow Control (FC) — ignored here, TX-side only
            pass

    def _send_fc(self):
        fc = bytes([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self._can.send(CANMessage(arb_id=self._tx_id, data=fc, is_rx=False))

    def _dispatch(self, payload: bytes):
        if self._rx_cb:
            self._rx_cb(payload)
