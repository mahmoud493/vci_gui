"""services/logging_service.py — GUI log routing via EventBus."""
import logging
from app.event_bus import bus

class GUILogHandler(logging.Handler):
    """Routes Python log records to the GUI console via EventBus."""

    LEVEL_MAP = {
        logging.DEBUG:    "DEBUG",
        logging.INFO:     "INFO",
        logging.WARNING:  "WARN",
        logging.ERROR:    "ERROR",
        logging.CRITICAL: "CRIT",
    }

    def emit(self, record: logging.LogRecord):
        try:
            level = self.LEVEL_MAP.get(record.levelno, "INFO")
            msg   = self.format(record)
            bus.log_message.emit(level, msg)
        except Exception:
            self.handleError(record)

def install_gui_log_handler(logger_name: str = "vci_pro"):
    handler = GUILogHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)-5s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logging.getLogger(logger_name).addHandler(handler)
