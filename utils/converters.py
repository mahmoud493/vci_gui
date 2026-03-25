"""utils/converters.py — Data conversion helpers"""
from typing import List

def bytes_to_hex(data: bytes, sep: str = " ") -> str:
    return sep.join(f"{b:02X}" for b in data)

def hex_to_bytes(s: str) -> bytes:
    s = s.replace(" ", "").replace("0x", "")
    return bytes.fromhex(s)

def uint_to_bytes(value: int, length: int, byteorder: str = "big") -> bytes:
    return value.to_bytes(length, byteorder)

def bytes_to_uint(data: bytes, byteorder: str = "big") -> int:
    return int.from_bytes(data, byteorder)

def decode_ascii(data: bytes) -> str:
    return data.decode("ascii", errors="replace").strip()

def baud_to_str(baud: int) -> str:
    if baud >= 1_000_000:
        return f"{baud / 1_000_000:.1f} Mbit/s"
    return f"{baud // 1000} kbit/s"

def scale_value(raw: int, factor: float, offset: float = 0.0) -> float:
    return raw * factor + offset
