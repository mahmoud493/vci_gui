"""communication/j2534_interface.py — J2534 PassThru PRO interface (Windows DLL)."""
import ctypes
import platform
from typing import Optional
from utils.logger import log

# J2534 Protocol IDs
J2534_CAN       = 0x05
J2534_ISO15765  = 0x06
J2534_CAN_FD    = 0x11

# Connect Flags
CAN_29BIT_ID    = 0x100
ISO15765_FRAME_PAD = 0x40

class J2534Error(Exception): pass

class J2534Interface:
    """
    Thin ctypes wrapper around a J2534 PassThru DLL.
    Requires a J2534-compliant VCI (e.g. Bosch VCI, Autel).
    Windows-only.
    """

    def __init__(self, dll_path: str = ""):
        self._dll: Optional[ctypes.WinDLL] = None  # type: ignore
        self._dll_path = dll_path
        self._device_id = ctypes.c_ulong(0)
        self._channel_id = ctypes.c_ulong(0)

    @property
    def available(self) -> bool:
        return platform.system() == "Windows"

    def open(self) -> bool:
        if not self.available:
            log.warning("J2534 not available (non-Windows platform)")
            return False
        try:
            self._dll = ctypes.WinDLL(self._dll_path)  # type: ignore
            ret = self._dll.PassThruOpen(None, ctypes.byref(self._device_id))
            if ret != 0:
                raise J2534Error(f"PassThruOpen failed: {ret}")
            log.info(f"J2534 device opened: {self._device_id.value}")
            return True
        except (OSError, AttributeError) as e:
            log.error(f"J2534 load failed: {e}")
            return False

    def connect(self, protocol: int = J2534_ISO15765, flags: int = 0,
                baud: int = 500000) -> bool:
        if not self._dll:
            return False
        ret = self._dll.PassThruConnect(
            self._device_id, protocol, flags,
            ctypes.c_ulong(baud), ctypes.byref(self._channel_id)
        )
        if ret != 0:
            log.error(f"PassThruConnect failed: {ret}")
            return False
        log.info(f"J2534 channel connected: {self._channel_id.value}")
        return True

    def close(self):
        if self._dll:
            self._dll.PassThruDisconnect(self._channel_id)
            self._dll.PassThruClose(self._device_id)
            log.info("J2534 device closed")

    @staticmethod
    def enumerate_devices() -> list:
        """Return list of J2534 device DLL paths from registry (Windows only)."""
        if platform.system() != "Windows":
            return []
        try:
            import winreg
            key_path = r"SOFTWARE\PassThruSupport.04.04"
            key      = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            devices  = []
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(key, i)
                    sub_key = winreg.OpenKey(key, sub)
                    dll, _ = winreg.QueryValueEx(sub_key, "FunctionLibrary")
                    devices.append((sub, dll))
                    i += 1
                except OSError:
                    break
            return devices
        except Exception as e:
            log.debug(f"J2534 registry scan: {e}")
            return []
