import os
import uuid
import json
import logging
import threading
from datetime import datetime

import redis
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

import redis_keys as K

logging.basicConfig(level=logging.INFO, format="%(asctime)s [web] %(message)s")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "docker-toolkit-secret")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

MAX_PAYLOAD_BYTES = 10_000

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
)


# ── Redis pub/sub listener (background thread) ────────────────────────────────
def _pubsub_listener() -> None:
    """Subscribe to scan_events channel and push updates to all WS clients."""
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe("scan_events")
    logging.info("Pub/sub listener started.")
    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            scan = json.loads(message["data"])
            socketio.emit("scan_update", scan)
            logging.info(f"WS emit scan_update → {scan['id']} [{scan['status']}]")
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(f"Bad pub/sub message: {e}")


threading.Thread(target=_pubsub_listener, daemon=True).start()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    try:
        visits = r.incr(K.VISITS)
    except redis.RedisError:
        visits = 0
    return render_template("index.html", visits=visits)


@app.route("/analyse", methods=["POST"])
def analyse():
    tool = request.form.get("tool", "").strip()
    payload = request.form.get("payload", "").strip()

    if not tool:
        return jsonify({"error": "No tool selected"}), 400
    if not payload:
        return jsonify({"error": "Config input is required"}), 400
    if len(payload) > MAX_PAYLOAD_BYTES:
        return jsonify({"error": f"Input too large (max {MAX_PAYLOAD_BYTES} chars)"}), 413

    scan = {
        "id": str(uuid.uuid4())[:8],
        "tool": tool,
        "payload": payload,
        "status": "pending",
        "result": "",
        "submitted": datetime.utcnow().strftime("%H:%M:%S"),
        "duration": "-",
    }

    try:
        r.lpush(K.SCAN_QUEUE, json.dumps(scan))
        r.hset(K.SCAN_RESULTS, scan["id"], json.dumps(scan))
        r.incr(K.TOTAL_SCANS)
        r.incr(K.PENDING_SCANS)
        # Push pending state immediately so UI shows card without waiting
        socketio.emit("scan_update", scan)
    except redis.RedisError as e:
        logging.error(f"Redis error on /analyse: {e}")
        return jsonify({"error": "Scanner unavailable, try again"}), 503

    logging.info(f"Queued scan {scan['id']} — {tool}")
    return jsonify({"scan_id": scan["id"], "status": "pending"})


@app.route("/scans")
def scans():
    try:
        raw = r.hvals(K.SCAN_RESULTS)
        items = sorted(
            [json.loads(s) for s in raw],
            key=lambda s: s.get("submitted", ""),
            reverse=True,
        )
        return jsonify(items)
    except redis.RedisError as e:
        logging.error(f"Redis error on /scans: {e}")
        return jsonify({"error": "Could not fetch scans"}), 503


@app.route("/stats")
def stats():
    keys = {
        "total": K.TOTAL_SCANS,
        "pending": K.PENDING_SCANS,
        "running": K.RUNNING_SCANS,
        "passed": K.PASSED_SCANS,
        "failed": K.FAILED_SCANS,
        "scanners": K.ACTIVE_SCANNERS,
        "visits": K.VISITS,
    }
    try:
        return jsonify({k: int(r.get(v) or 0) for k, v in keys.items()})
    except redis.RedisError as e:
        logging.error(f"Redis error on /stats: {e}")
        return jsonify({"error": "Could not fetch stats"}), 503


@app.route("/clear", methods=["POST"])
def clear():
    try:
        r.delete(K.SCAN_QUEUE, K.SCAN_RESULTS)
        for key in [K.PENDING_SCANS, K.TOTAL_SCANS, K.PASSED_SCANS,
                    K.FAILED_SCANS, K.RUNNING_SCANS]:
            r.set(key, 0)
        socketio.emit("feed_cleared")
        logging.info("Scan queue cleared")
        return jsonify({"status": "cleared"})
    except redis.RedisError as e:
        logging.error(f"Redis error on /clear: {e}")
        return jsonify({"error": "Could not clear queue"}), 503


# ── Socket.IO events ──────────────────────────────────────────────────────────
@socketio.on("connect")
def on_connect():
    logging.info("Client connected via WebSocket")


@socketio.on("disconnect")
def on_disconnect():
    logging.info("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
