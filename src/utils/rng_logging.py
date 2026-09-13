"""Seeded RNG + structured logging. Determinism: moi randomness qua ham nay."""
from __future__ import annotations

import json
import logging
import sys
import numpy as np

_configured = False


def get_logger(name: str) -> logging.Logger:
    global _configured
    logger = logging.getLogger(name)
    if not _configured:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(message)s"))
        logging.root.addHandler(h)
        logging.root.setLevel(logging.INFO)
        _configured = True
    return logger


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    logger.info(json.dumps({"event": event, **fields}))


def seeded_rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)
