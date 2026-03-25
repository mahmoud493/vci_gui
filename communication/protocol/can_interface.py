"""communication/protocol/can_interface.py — Abstract CAN interface."""
from abc import ABC, abstractmethod
from typing import Optional, Callable
from models.message import CANMessage

class CANInterface(ABC):
    def __init__(self):
        self._rx_callback: Optional[Callable[[CANMessage], None]] = None

    def set_rx_callback(self, cb: Callable[[CANMessage], None]):
        self._rx_callback = cb

    @abstractmethod
    def send(self, msg: CANMessage) -> bool: ...

    @abstractmethod
    def start(self) -> bool: ...

    @abstractmethod
    def stop(self): ...

    @abstractmethod
    def is_open(self) -> bool: ...
