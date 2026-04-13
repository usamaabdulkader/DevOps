import os
import json
import time
import logging
import atexit
import signal
import sys
import threading

import redis

import redis_keys as K
from tools import run_tool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [scanner] %(message)s")

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)

FAIL_GRADES = {"HIGH RISK", "CRITICAL RISK", "BLOATED"}


def register():
    r.set(K.ACTIVE_SCANNERS, 1)
    r.publish("scan_events", json.dumps({"type": "scanner_up"}))
    logging.info("Scanner ready.")


def deregister():
    r.set(K.ACTIVE_SCANNERS, 0)
    r.publish("scan_events", json.dumps({"type": "scanner_down"}))
    logging.info("Scanner offline.")


def handle_shutdown(signum, frame):
    deregister()
    sys.exit(0)


def _heartbeat():
    while True:
        r.set(K.ACTIVE_SCANNERS, 1, ex=15)
        time.sleep(8)


def _publish(scan: dict) -> None:
    """Publish scan state to Redis pub/sub so app.py can push it via WebSocket."""
    r.publish("scan_events", json.dumps(scan))


def _derive_status(result: str) -> str:
    """
    Determine pass/fail from a tool result string.

    Two result formats exist:
      1. Pipe-delimited text  →  check for [ERR] / [FAIL] tokens
      2. JSON (image_size / security_scan)  →  check the 'grade' field
    """
    try:
        data = json.loads(result)
        if isinstance(data, dict) and data.get("grade") in FAIL_GRADES:
            return "failed"
        return "passed"
    except (json.JSONDecodeError, TypeError):
        pass

    lines = result.split(" | ")
    has_errors = any(
        l.strip().startswith("[ERR]") or l.strip().startswith("[FAIL]")
        for l in lines
    )
    return "failed" if has_errors else "passed"


def run_scan(scan: dict) -> None:
    scan["status"] = "running"
    r.hset(K.SCAN_RESULTS, scan["id"], json.dumps(scan))
    r.decr(K.PENDING_SCANS)
    r.incr(K.RUNNING_SCANS)
    _publish(scan)

    start = time.time()
    try:
        scan["result"] = run_tool(scan["tool"], scan["payload"])
        scan["status"] = _derive_status(scan["result"])

        if scan["status"] == "failed":
            r.incr(K.FAILED_SCANS)
        else:
            r.incr(K.PASSED_SCANS)

    except Exception as e:
        scan["result"] = str(e)
        scan["status"] = "failed"
        r.incr(K.FAILED_SCANS)
    finally:
        scan["duration"] = str(round(time.time() - start, 2))
        r.hset(K.SCAN_RESULTS, scan["id"], json.dumps(scan))
        r.decr(K.RUNNING_SCANS)
        _publish(scan)

    logging.info(f"Scan {scan['id']} → {scan['status']} ({scan['duration']}s)")


def main() -> None:
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    register()
    atexit.register(deregister)

    threading.Thread(target=_heartbeat, daemon=True).start()

    logging.info("Listening for scans…")

    while True:
        item = r.brpop(K.SCAN_QUEUE, timeout=5)
        if item is None:
            continue
        _, raw = item
        try:
            scan = json.loads(raw)
        except json.JSONDecodeError:
            logging.warning("Malformed scan payload — skipping")
            continue
        logging.info(f"Running {scan['id']} — {scan['tool']}")
        run_scan(scan)


if __name__ == "__main__":
    main()