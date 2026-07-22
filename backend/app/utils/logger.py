"""Structured logging with structlog.

Every log line is a JSON object with: timestamp, level, logger, event, and context.
"""

import logging
import sys
from pathlib import Path

import structlog


def setup_logging(name: str = "careerforge", level: str = "INFO") -> structlog.BoundLogger:
    """Configure and return a structlog logger.

    Logs go to:
    - stdout (always)
    - logs/careerforge.log (rotated, JSON)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Ensure log directory exists
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        level=log_level,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "careerforge.log", encoding="utf-8"),
        ],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger(name)
