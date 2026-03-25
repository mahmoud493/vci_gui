"""core/dtc_parser.py — Parse UDS DTC responses (SID 0x59)."""
from typing import List
from models.dtc import DTC, DTCSeverity
from utils.logger import log

class DTCParser:
    @staticmethod
    def parse_read_dtc_response(data: bytes) -> List[DTC]:
        """
        Parse response to ReadDTCInformation (0x59 02 ...).
        data = raw UDS response bytes starting with 0x59.
        Returns list of DTC objects.
        """
        dtcs: List[DTC] = []
        if not data or data[0] != 0x59:
            log.warning(f"DTCParser: unexpected response: {data.hex()}")
            return dtcs
        # Byte 1 = sub-function, Byte 2 = status_availability_mask
        if len(data) < 3:
            return dtcs
        idx = 3  # start of DTC records
        record_len = 4  # 3 DTC bytes + 1 status byte
        while idx + record_len <= len(data):
            raw_code    = int.from_bytes(data[idx:idx + 3], "big")
            status_byte = data[idx + 3]
            dtc = DTC(code=raw_code, status_byte=status_byte)
            dtcs.append(dtc)
            idx += record_len
        log.debug(f"DTCParser: parsed {len(dtcs)} DTCs")
        return dtcs

    @staticmethod
    def lookup_description(dtc_code: str) -> str:
        """Simple lookup table — extend with OEM database."""
        table = {
            "P0100": "Mass or Volume Air Flow Circuit Malfunction",
            "P0110": "Intake Air Temperature Circuit Malfunction",
            "P0115": "Engine Coolant Temperature Circuit Malfunction",
            "P0120": "Throttle/Pedal Position Sensor A Circuit Malfunction",
            "P0130": "O2 Sensor Circuit Malfunction (Bank 1 Sensor 1)",
            "P0300": "Random/Multiple Cylinder Misfire Detected",
            "P0301": "Cylinder 1 Misfire Detected",
            "P0400": "Exhaust Gas Recirculation Flow Malfunction",
            "P0420": "Catalyst System Efficiency Below Threshold (Bank 1)",
            "P0500": "Vehicle Speed Sensor Malfunction",
            "P0600": "Serial Communication Link Malfunction",
            "P0700": "Transmission Control System Malfunction",
            "C0035": "Right Front Wheel Speed Sensor Circuit",
            "C0040": "Right Rear Wheel Speed Sensor Circuit",
            "U0001": "High Speed CAN Communication Bus",
            "U0100": "Lost Communication With ECM/PCM",
            "U0121": "Lost Communication With Anti-Lock Brake System",
            "U0140": "Lost Communication With Body Control Module",
            "U0155": "Lost Communication With Instrument Panel Cluster",
        }
        return table.get(dtc_code, "Description not available")
