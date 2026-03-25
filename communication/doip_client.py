"""communication/doip_client.py — DoIP (ISO 13400-2) transport client."""
import socket
import struct
import threading
from typing import Optional, Callable
from utils.constants import DOIP_TCP_PORT, DOIP_VERSION
from utils.logger import log

# DoIP payload types
PT_VEHICLE_ID_REQ          = 0x0001
PT_VEHICLE_ID_RESP         = 0x0004
PT_ROUTING_ACTIVATION_REQ  = 0x0005
PT_ROUTING_ACTIVATION_RESP = 0x0006
PT_ALIVE_CHECK_REQ         = 0x0007
PT_ALIVE_CHECK_RESP        = 0x0008
PT_DIAG_MESSAGE            = 0x8001
PT_DIAG_MESSAGE_ACK        = 0x8002
PT_DIAG_MESSAGE_NACK       = 0x8003

class DoIPClient:
    HEADER_LEN = 8

    def __init__(self, host: str, port: int = DOIP_TCP_PORT,
                 source_address: int = 0x0E00,
                 target_address: int = 0x0001):
        self._host     = host
        self._port     = port
        self._src_addr = source_address
        self._tgt_addr = target_address
        self._sock:    Optional[socket.socket] = None
        self._thread:  Optional[threading.Thread] = None
        self._running  = False
        self._rx_cb:   Optional[Callable[[bytes], None]] = None

    def set_rx_callback(self, cb: Callable[[bytes], None]):
        self._rx_cb = cb

    def connect(self) -> bool:
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(5.0)
            self._sock.connect((self._host, self._port))
            self._running = True
            self._thread  = threading.Thread(target=self._rx_loop, daemon=True)
            self._thread.start()
            return self._routing_activation()
        except OSError as e:
            log.error(f"DoIP connect failed: {e}")
            return False

    def disconnect(self):
        self._running = False
        if self._sock:
            self._sock.close()

    def send_uds(self, data: bytes) -> bool:
        payload = struct.pack(">HH", self._src_addr, self._tgt_addr) + data
        return self._send(PT_DIAG_MESSAGE, payload)

    # ── Internal ─────────────────────────────────────────────────────────
    def _send(self, payload_type: int, payload: bytes) -> bool:
        header = struct.pack(">BBHI",
                             DOIP_VERSION, ~DOIP_VERSION & 0xFF,
                             payload_type, len(payload))
        try:
            self._sock.sendall(header + payload)
            return True
        except OSError as e:
            log.error(f"DoIP TX error: {e}")
            return False

    def _routing_activation(self) -> bool:
        payload = struct.pack(">HBL", self._src_addr, 0x00, 0x00000000)
        self._send(PT_ROUTING_ACTIVATION_REQ, payload)
        # Response handled in _rx_loop
        return True

    def _rx_loop(self):
        buf = b""
        while self._running:
            try:
                chunk = self._sock.recv(4096)
                if not chunk:
                    break
                buf += chunk
                buf = self._parse(buf)
            except OSError:
                break

    def _parse(self, buf: bytes) -> bytes:
        while len(buf) >= self.HEADER_LEN:
            ptype  = struct.unpack_from(">H", buf, 2)[0]
            length = struct.unpack_from(">I", buf, 4)[0]
            if len(buf) < self.HEADER_LEN + length:
                break
            payload = buf[self.HEADER_LEN: self.HEADER_LEN + length]
            if ptype == PT_DIAG_MESSAGE_ACK or ptype == PT_DIAG_MESSAGE:
                if self._rx_cb and len(payload) >= 4:
                    self._rx_cb(payload[4:])   # strip src+tgt addr
            buf = buf[self.HEADER_LEN + length:]
        return buf
