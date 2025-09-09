"""Configuration utilities for PortForwardPi."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


Config = Dict[str, Any]


DEFAULT_CONFIG: Config = {
    "forwards": [],
    "allow_ips": [],
    "block_ips": [],
    "allow_countries": [],
    "block_countries": [],
}


def load_config(path: str | Path) -> Config:
    """Load configuration from *path*.

    Missing files result in :data:`DEFAULT_CONFIG`.
    """
    p = Path(path)
    if not p.exists():
        return DEFAULT_CONFIG.copy()
    with p.open() as f:
        data = json.load(f)
    # Ensure all keys exist even if file is from an older version
    cfg = DEFAULT_CONFIG.copy()
    cfg.update(data)
    return cfg


def save_config(path: str | Path, config: Config) -> None:
    """Save *config* to *path* in JSON format."""
    p = Path(path)
    with p.open("w") as f:
        json.dump(config, f, indent=2)
