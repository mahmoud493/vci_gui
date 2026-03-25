"""communication/usb_transport.py — USB CDC transport to STM32H723 VCI."""
import threading
import queue
import serial
import serial.tools.list_ports
from typing import Optional, List
from models.message import CANMessage
from .protocol.can_interface import CANInterface
from utils.logger import log

# ── Simple framing: <STX><LEN_H><LEN_L><PAYLOAD><ETX> ────────────────────────
STX = 0xAA
ETX = 0x55

class USBTransport(CANInterface):
    """Serial/USB CDC interface to the STM32 VCI firmware."""

    def __init__(self, port: str = "", baudrate: int = 115200):
        super().__init__()
        self._port     = port
        self._baudrate = baudrate
        self._ser:     Optional[serial.Serial] = None
        self._rx_thread: Optional[threading.Thread] = None
        self._running  = False
        self._tx_queue: queue.Queue = queue.Queue()

    # ── CANInterface implementation ────────────────────────────────────────
    def start(self) -> bool:
        try:
            self._ser = serial.Serial(
                port=self._port, baudrate=self._baudrate,
                timeout=0.1, write_timeout=1.0
            )
            self._running   = True
            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._rx_thread.start()
            log.info(f"USB transport opened: {self._port} @ {self._baudrate}")
            return True
        except serial.SerialException as e:
            log.error(f"USB open failed: {e}")
            return False

    def stop(self):
        self._running = False
        if self._ser and self._ser.is_open:
            self._ser.close()
        log.info("USB transport closed")

    def is_open(self) -> bool:
        return self._ser is not None and self._ser.is_open

    def send(self, msg: CANMessage) -> bool:
        if not self.is_open():
            return False
        try:
            payload = self._encode_frame(msg)
            self._ser.write(payload)
            return True
        except serial.SerialException as e:
            log.error(f"USB TX error: {e}")
            return False

    # ── Helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def list_ports() -> List[str]:
        return [p.device for p in serial.tools.list_ports.comports()]
        print(USBTransport.list_ports())

    def _encode_frame(self, msg: CANMessage) -> bytes:
        """Pack a CANMessage into the wire format expected by VCI firmware."""
        arb_bytes = msg.arb_id.to_bytes(4, "big")
        flags     = 0x01 if msg.is_fd else 0x00
        payload   = arb_bytes + bytes([flags, msg.dlc]) + bytes(msg.data)
        length    = len(payload)
        frame     = bytes([STX, (length >> 8) & 0xFF, length & 0xFF]) + payload + bytes([ETX])
        return frame

    def _rx_loop(self):
        buf = bytearray()
        while self._running:
            if not self._ser or not self._ser.is_open:
                break
            try:
                chunk = self._ser.read(64)
                if chunk:
                    buf.extend(chunk)
                    buf = self._parse_frames(buf)
            except serial.SerialException as e:
                log.error(f"USB RX error: {e}")
                break

    def _parse_frames(self, buf: bytearray) -> bytearray:
        while len(buf) >= 4:
            if buf[0] != STX:
                buf.pop(0)
                continue
            if len(buf) < 3:
                break
            length = (buf[1] << 8) | buf[2]
            total  = 3 + length + 1
            if len(buf) < total:
                break
            if buf[total - 1] != ETX:
                buf.pop(0)
                continue
            payload = bytes(buf[3:3 + length])
            self._dispatch_frame(payload)
            del buf[:total]
        return buf

    def _dispatch_frame(self, payload: bytes):
        if len(payload) < 6:
            return
        arb_id = int.from_bytes(payload[:4], "big")
        flags  = payload[4]
        dlc    = payload[5]
        data   = payload[6:6 + dlc]
        msg    = CANMessage(arb_id=arb_id, data=data, is_fd=bool(flags & 0x01), dlc=dlc)
        if self._rx_callback:
            self._rx_callback(msg)
