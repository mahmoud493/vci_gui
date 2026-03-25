"""app/state_manager.py — Global application state."""
from dataclasses import dataclass, field
from typing import Optional, List
from models.vehicle import Vehicle
from models.ecu import ECU
from models.dtc import DTC

@dataclass
class AppState:
    # Connection
    connected: bool = False
    transport: str = ""          # "USB", "DoIP", "J2534"
    transport_desc: str = ""

    # Vehicle / ECU
    vehicle: Vehicle = field(default_factory=Vehicle)
    selected_ecu: Optional[ECU] = None

    # Diagnostic
    dtc_list: List[DTC] = field(default_factory=list)
    live_data: dict = field(default_factory=dict)
    session_active: bool = False
    current_session: int = 0x01

    # Bus monitor
    frame_filter: str = ""
    monitor_active: bool = False

    def reset(self):
        self.connected        = False
        self.transport        = ""
        self.transport_desc   = ""
        self.vehicle          = Vehicle()
        self.selected_ecu     = None
        self.dtc_list         = []
        self.live_data        = {}
        self.session_active   = False
        self.current_session  = 0x01

# Global singleton
state = AppState()
