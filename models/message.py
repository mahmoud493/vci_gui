"""models/message.py — CAN / UDS raw message model"""
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class CANMessage:
    arb_id: int
    data: bytes
    timestamp: float = field(default_factory=time.monotonic)
    is_fd: bool = False
    is_rx: bool = True
    channel: str = "CAN1"
    dlc: int = 0

    def __post_init__(self):
        if not self.dlc:
            self.dlc = len(self.data)

    @property
    def arb_id_hex(self) -> str:
        return f"{self.arb_id:08X}" if self.arb_id > 0x7FF else f"{self.arb_id:03X}"

    @property
    def data_hex(self) -> str:
        return " ".join(f"{b:02X}" for b in self.data)

    @property
    def timestamp_ms(self) -> str:
        return f"{self.timestamp * 1000:.3f}"


"""models/vehicle.py — Top-level vehicle model"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .ecu import ECU

@dataclass
class Vehicle:
    vin: str = ""
    make: str = ""
    model: str = ""
    year: int = 0
    protocol: str = ""          # CAN-FD / DoIP / K-Line / LIN
    bus_speed: int = 500000     # bits/s
    ecus: List[ECU] = field(default_factory=list)
    live_data: Dict[str, float] = field(default_factory=dict)

    def get_ecu(self, address: int) -> Optional[ECU]:
        for ecu in self.ecus:
            if ecu.address == address:
                return ecu
        return None

    def add_ecu(self, ecu: ECU):
        if not self.get_ecu(ecu.address):
            self.ecus.append(ecu)

    @property
    def total_dtc_count(self) -> int:
        return sum(e.dtc_count for e in self.ecus)

    @property
    def vin_display(self) -> str:
        return self.vin if self.vin else "NOT READ"
