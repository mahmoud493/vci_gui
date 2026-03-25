"""models/ecu.py — ECU data model"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class ECUStatus(Enum):
    UNKNOWN   = "unknown"
    PRESENT   = "present"
    ACTIVE    = "active"
    NO_RESP   = "no_response"
    ERROR     = "error"

@dataclass
class ECU:
    address: int                        # UDS target address (e.g. 0x7E0)
    name: str = "Unknown ECU"
    ecu_id: str = ""                    # e.g. "ENG", "ABS"
    sw_version: str = ""
    hw_version: str = ""
    supplier_id: str = ""
    status: ECUStatus = ECUStatus.UNKNOWN
    dtc_count: int = 0
    supported_services: list = field(default_factory=list)
    session_active: bool = False
    protocol: str = "UDS"               # UDS / KWP2000

    @property
    def address_hex(self) -> str:
        return f"0x{self.address:03X}"
