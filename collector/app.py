"""Metrics Collector — Flask API on port 6000.

Endpoints:
  GET /status   — JSON snapshot of system metrics (called by the dashboard).
  GET /health   — Liveness check used by `docker compose ps` / curl.
  GET /metrics  — JSON list of recent snapshots persisted to /data/metrics.json.

The /data directory is mounted from the `metrics_data` Docker volume,
so snapshot history survives container restarts.
"""

from __future__ import annotations

import json
import os
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask, jsonify

import metrics

DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
SNAPSHOT_FILE = DATA_DIR / "metrics.json"
MAX_SNAPSHOTS = 100

app = Flask(__name__)


def _persist_snapshot(snapshot: Dict[str, Any]) -> None:
    """Append a snapshot to the JSON history file on the mounted volume."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        history: List[Dict[str, Any]] = []
        if SNAPSHOT_FILE.exists():
            try:
                history = json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8"))
                if not isinstance(history, list):
                    history = []
            except json.JSONDecodeError:
                history = []

        history.append(snapshot)
        # Keep only the latest MAX_SNAPSHOTS entries.
        history = history[-MAX_SNAPSHOTS:]
        SNAPSHOT_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — never crash the API on disk errors
        app.logger.warning("Failed to persist snapshot: %s", exc)


@app.route("/status", methods=["GET"])
def status() -> Any:
    """Return current metrics and persist a snapshot to the volume."""
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "container": socket.gethostname(),
        **metrics.collect(),
    }
    _persist_snapshot(snapshot)
    return jsonify(snapshot)


@app.route("/health", methods=["GET"])
def health() -> Any:
    """Liveness probe."""
    return jsonify({"ok": True, "service": "collector"})


@app.route("/metrics", methods=["GET"])
def history() -> Any:
    """Return the persisted snapshot history (last MAX_SNAPSHOTS entries)."""
    if not SNAPSHOT_FILE.exists():
        return jsonify([])
    try:
        return jsonify(json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8")))
    except json.JSONDecodeError:
        return jsonify([])


@app.route("/", methods=["GET"])
def root() -> Any:
    """Default route — small JSON index of available endpoints."""
    return jsonify(
        {
            "service": "metrics-collector",
            "endpoints": ["/status", "/health", "/metrics"],
        }
    )


if __name__ == "__main__":
    # Listen on all interfaces inside the container so the dashboard
    # (on the same Docker network) can reach us via container DNS.
    app.run(host="0.0.0.0", port=6000)
