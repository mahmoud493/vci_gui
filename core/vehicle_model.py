"""core/vehicle_model.py — Vehicle-level data model with live data definitions."""
from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class LiveDataDef:
    did: int
    name: str
    unit: str
    factor: float = 1.0
    offset: float = 0.0
    min_val: float = 0.0
    max_val: float = 100.0
    byte_len: int = 2

STANDARD_LIVE_DATA: Dict[str, LiveDataDef] = {
    "ENGINE_RPM":      LiveDataDef(0x010C, "Engine RPM",       "rpm",  0.25, 0, 0, 8000, 2),
    "VEHICLE_SPEED":   LiveDataDef(0x010D, "Vehicle Speed",    "km/h", 1.0,  0, 0, 300,  1),
    "COOLANT_TEMP":    LiveDataDef(0x0105, "Coolant Temp",     "°C",   1.0, -40, -40, 215, 1),
    "INTAKE_TEMP":     LiveDataDef(0x010F, "Intake Air Temp",  "°C",   1.0, -40, -40, 215, 1),
    "MAF":             LiveDataDef(0x0110, "MAF Air Flow",     "g/s",  0.01, 0, 0, 655, 2),
    "THROTTLE_POS":    LiveDataDef(0x0111, "Throttle Position","%" ,   0.392, 0, 0, 100, 1),
    "FUEL_PRESSURE":   LiveDataDef(0x010A, "Fuel Pressure",    "kPa",  3.0, 0, 0, 765, 1),
    "BATTERY_VOLTAGE": LiveDataDef(0x0142, "Battery Voltage",  "V",    0.001, 0, 0, 65.5, 2),
    "ENGINE_LOAD":     LiveDataDef(0x0104, "Engine Load",      "%",    0.392, 0, 0, 100, 1),
    "FUEL_TRIM_ST_B1": LiveDataDef(0x0106, "STFT Bank 1",      "%",    0.781, -100, -100, 99.2, 1),
    "FUEL_TRIM_LT_B1": LiveDataDef(0x0107, "LTFT Bank 1",      "%",    0.781, -100, -100, 99.2, 1),
    "O2_SENSOR_B1S1":  LiveDataDef(0x0114, "O2 Sensor B1S1",   "V",    0.005, 0, 0, 1.275, 1),
}
