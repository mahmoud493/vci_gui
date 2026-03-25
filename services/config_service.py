"""services/config_service.py — Persistent application configuration."""
import json
from pathlib import Path
from typing import Any
from utils.logger import log

CONFIG_FILE = Path("vci_config.json")

_defaults = {
    "transport":          "USB",
    "usb_port":           "",
    "usb_baudrate":       115200,
    "doip_host":          "192.168.1.1",
    "doip_port":          13400,
    "doip_src_addr":      0x0E00,
    "doip_tgt_addr":      0x0001,
    "j2534_dll":          "",
    "can_bitrate":        500000,
    "scan_addr_start":    0x700,
    "scan_addr_end":      0x77F,
    "log_level":          "DEBUG",
    "theme":              "dark",
    "live_data_interval": 100,
}

class ConfigService:
    def __init__(self):
        self._data: dict = dict(_defaults)
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data.update(loaded)
                log.debug("Config loaded")
            except Exception as e:
                log.warning(f"Config load failed: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2)
            log.debug("Config saved")
        except Exception as e:
            log.error(f"Config save failed: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any):
        self._data[key] = value

    def __getitem__(self, key):  return self._data[key]
    def __setitem__(self, key, v): self._data[key] = v

config = ConfigService()
