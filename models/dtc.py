"""models/dtc.py — Diagnostic Trouble Code model"""
from dataclasses import dataclass
from enum import Enum

class DTCSeverity(Enum):
    NO_FAULT        = 0x00
    MAINTENANCE_REQ = 0x20
    CHECK_AT_NEXT   = 0x40
    CHECK_IMMED     = 0x50
    FAULT           = 0x60

class DTCStatus(Enum):
    ACTIVE    = "active"
    PENDING   = "pending"
    STORED    = "stored"
    PERMANENT = "permanent"

@dataclass
class DTC:
    code: int               # Raw 3-byte DTC code
    status_byte: int = 0x00
    severity: DTCSeverity = DTCSeverity.NO_FAULT
    functional_unit: int = 0x00
    ecu_address: int = 0x00
    description: str = ""

    @property
    def code_str(self) -> str:
        """Format as P/C/B/U + 4 hex digits (ISO 15031-6)."""
        prefix_map = {0b00: 'P', 0b01: 'C', 0b10: 'B', 0b11: 'U'}
        prefix = prefix_map[(self.code >> 14) & 0x03]
        sub    = (self.code >> 12) & 0x03
        num    = self.code & 0x0FFF
        return f"{prefix}{sub}{num:04X}"

    @property
    def status(self) -> DTCStatus:
        if self.status_byte & 0x01:
            return DTCStatus.ACTIVE
        if self.status_byte & 0x04:
            return DTCStatus.PENDING
        if self.status_byte & 0x10:
            return DTCStatus.PERMANENT
        return DTCStatus.STORED

    @property
    def test_failed(self) -> bool:
        return bool(self.status_byte & 0x01)

    @property
    def confirmed(self) -> bool:
        return bool(self.status_byte & 0x08)
