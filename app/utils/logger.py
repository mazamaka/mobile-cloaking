"""Loguru logger configuration for the application."""

import sys

from loguru import logger

from config import SETTINGS


def setup_logger() -> None:
    """Configure loguru with colored output and appropriate log level."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if SETTINGS.debug else "INFO",
        colorize=True,
    )


setup_logger()

__all__ = ["logger"]
