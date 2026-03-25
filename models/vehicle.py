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
    protocol: str = ""
    bus_speed: int = 500000
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
