import json
import logging
import sys


def setup_logging() -> logging.Logger:
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter("%(message)s"))
    log = logging.getLogger("ajanta")
    log.handlers = [h]
    log.setLevel(logging.INFO)
    return log


def event(name: str, **fields) -> None:
    """Structured log line. Never pass raw personal data."""
    logging.getLogger("ajanta").info(json.dumps({"event": name, **fields}))
