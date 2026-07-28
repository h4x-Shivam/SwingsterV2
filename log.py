"""
log.py — Centralized logging configuration for SwingsterV2.

Call ``setup_logging()`` once at application startup (in main.py or
api_server.py) before any other imports that use logging.

All modules should use ``get_logger(__name__)`` to obtain their logger,
which produces hierarchical names like ``swingster.scanner.engine``.
"""

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging for the entire application.

    Sets up a single StreamHandler on the ``swingster`` root logger
    with a consistent format across all modules.
    """
    root = logging.getLogger("swingster")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers if called multiple times
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger under the ``swingster`` namespace.

    Usage::

        from log import get_logger
        logger = get_logger(__name__)
        logger.info("Scan started")
    """
    return logging.getLogger(f"swingster.{name}")
