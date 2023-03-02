# coding=utf-8
"""
Convenience functions
"""
# Standard Library
import logging
from pathlib import Path


def get_project_root() -> Path:
    """This is needed to ensure we find our root-level config and other files"""
    return Path(__file__).parent.parent


def create_logger(debug: bool = False) -> logging.Logger:
    """
    Logging setup
    with help from https://docs.python.org/3/howto/logging-cookbook.html
    """
    if debug:
        loglevel = logging.DEBUG
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] (%(funcName)s:%(lineno)s) %(message)s"
        )
    else:
        loglevel = logging.INFO
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    logger = logging.getLogger("main")
    logger.setLevel(loglevel)

    loghandler = logging.StreamHandler()
    loghandler.setFormatter(formatter)

    logger.addHandler(loghandler)
    return logger
