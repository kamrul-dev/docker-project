"""System metric collectors.

Tiny helpers around `psutil` that return scalar values safe for JSON
serialization. All functions are pure-ish: they read current state and
return a native Python type (int or float).
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict

import psutil

# Container/process start time is captured once at module import. This gives
# a stable "uptime" value that does not drift between requests.
_BOOT_TIME = time.time()


def cpu_percent() -> float:
    """Return current process CPU usage as a percentage.

    `psutil.Process(os.getpid()).cpu_percent(interval=None)` samples since
    the last call; the first call returns 0.0, which is fine for our use.
    """
    try:
        return round(float(psutil.Process(os.getpid()).cpu_percent(interval=None)), 2)
    except Exception:
        return 0.0


def memory_percent() -> float:
    """Return current process memory usage as a percentage of total host memory."""
    try:
        return round(float(psutil.Process(os.getpid()).memory_percent()), 2)
    except Exception:
        return 0.0


def disk_percent(path: str = "/") -> float:
    """Return disk usage at the given mount point as a percentage."""
    try:
        return round(float(psutil.disk_usage(path).percent), 2)
    except Exception:
        return 0.0


def uptime_seconds() -> int:
    """Seconds since this module was imported (proxy for container uptime)."""
    return int(time.time() - _BOOT_TIME)


def hostname() -> str:
    """Container hostname — useful for verifying which container responded."""
    try:
        return str(psutil.os.uname().nodename)
    except Exception:
        return os.uname().nodename  # type: ignore[attr-defined]


def collect() -> Dict[str, Any]:
    """Return a JSON-safe snapshot of all metrics."""
    return {
        "hostname": hostname(),
        "cpu_percent": cpu_percent(),
        "memory_percent": memory_percent(),
        "disk_percent": disk_percent("/"),
        "uptime_seconds": uptime_seconds(),
    }
