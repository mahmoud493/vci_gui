"""utils/logger.py — Centralized logging setup"""
import logging
import sys
from pathlib import Path

LOG_FILE = Path("vci_pro.log")

def setup_logger(name: str = "vci_pro", level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)

    fmt = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] [%(levelname)-8s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S"
    )

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(fmt)

    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger

log = setup_logger()
