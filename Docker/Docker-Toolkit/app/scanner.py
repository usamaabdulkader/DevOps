import os
import json
import time
import logging
import atexit

import redis

import redis_keys as K
from tools import run_tool

logging.basicConfig(level=logging.INFO, format="%(asctime)s [scanner] %(message)s")

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


def register() -> None:
    r.set(K.ACTIVE_SCANNERS, 1)
    logging.info("Scanner ready.")


def deregister() -> None:
    r.set(K.ACTIVE_SCANNERS, 0)
    logging.info("Scanner offline.")


def _publish(scan: dict) -> None:
    """Publish scan state to Redis pub/sub so app.py can push it via WebSocket."""
    r.publish("scan_events", json.dumps(scan))


def run_scan(scan: dict) -> None:
    # Mark as running
    scan["status"] = "running"
    r.hset(K.SCAN_RESULTS, scan["id"], json.dumps(scan))
    r.decr(K.PENDING_SCANS)
    r.incr(K.RUNNING_SCANS)
    _publish(scan)

    start = time.time()
    try:
        scan["result"] = run_tool(scan["tool"], scan["payload"])
        
        # ✅ FIX: derive status from result content, not just exception
        result_lines = scan["result"].split(" | ")
        has_errors = any(
            l.strip().startswith("[ERR]") or l.strip().startswith("[FAIL]")
            for l in result_lines
        )
        if has_errors:
            scan["status"] = "failed"
            r.incr(K.FAILED_SCANS)
        else:
            scan["status"] = "passed"
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
    register()
    atexit.register(deregister)
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
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scanner interrupted.")
