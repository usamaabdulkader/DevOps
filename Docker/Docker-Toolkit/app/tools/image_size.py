"""
Image Size Analyser — inspects a built local image using Docker CLI.
Returns a JSON string so the dashboard can render a rich layout.

Requires:
  - Docker CLI inside the container
  - /var/run/docker.sock mounted read-only
"""
import json
import shutil
import subprocess


def _fmt_mb(size_bytes: int) -> str:
    return f"{round(size_bytes / 1_048_576, 1)} MB"


def _grade(total_mb: float) -> str:
    if total_mb < 200:  return "LEAN"
    if total_mb < 500:  return "OK"
    if total_mb < 900:  return "HEAVY"
    return "BLOATED"


def _parse_size(size_str: str) -> float:
    """Convert Docker size string (e.g. '210MB', '1.2GB') to MB."""
    s = size_str.strip().upper()
    if s in ("0B", ""):  return 0.0
    if s.endswith("GB"): return float(s[:-2]) * 1024
    if s.endswith("MB"): return float(s[:-2])
    if s.endswith("KB"): return float(s[:-2]) / 1024
    if s.endswith("B"):  return float(s[:-1]) / 1_048_576
    return 0.0


def _clean_cmd(created_by: str) -> str:
    cmd = (created_by or "").strip()
    for prefix in ("/bin/sh -c ", "#(nop) "):
        if cmd.startswith(prefix):
            cmd = cmd[len(prefix):]
    return cmd or "<unknown>"


def analyze_image_size(content: str) -> str:
    image = content.strip()
    if not image:
        raise RuntimeError("Provide an image name, e.g. myapp:latest")

    if not shutil.which("docker"):
        raise RuntimeError(
            "Docker CLI not found — install docker-ce-cli and mount /var/run/docker.sock"
        )

    probe = subprocess.run(["docker", "version"], capture_output=True, timeout=8)
    if probe.returncode != 0:
        raise RuntimeError("Docker daemon not reachable — check socket mount")

    # ── Total size via inspect ─────────────────────────────────
    inspect = subprocess.run(
        ["docker", "image", "inspect", image, "--format", "{{json .}}"],
        capture_output=True, text=True, timeout=15,
    )
    if inspect.returncode != 0:
        raise RuntimeError(f"Image '{image}' not found locally — build or pull it first")

    meta        = json.loads(inspect.stdout)
    total_bytes = meta.get("Size", 0) or 0
    total_mb    = round(total_bytes / 1_048_576, 1)
    grade       = _grade(total_mb)

    # ── Layer breakdown via history ────────────────────────────
    hist = subprocess.run(
        ["docker", "history", "--no-trunc", "--format", "{{json .}}", image],
        capture_output=True, text=True, timeout=15,
    )

    layers = []
    if hist.returncode == 0:
        for line in hist.stdout.splitlines():
            try:
                row = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            size_mb = _parse_size(row.get("Size", "0B"))
            if size_mb > 0:
                layers.append({
                    "size_mb":  round(size_mb, 1),
                    "size_raw": row.get("Size", ""),
                    "cmd":      _clean_cmd(row.get("CreatedBy", "")),
                })

    top5 = sorted(layers, key=lambda x: x["size_mb"], reverse=True)[:5]
    max_mb = top5[0]["size_mb"] if top5 else 1

    result = {
        "__type":      "image_size",
        "image":       image,
        "total_mb":    total_mb,
        "grade":       grade,
        "layer_count": len(layers),
        "layers": [
            {
                "rank":    i + 1,
                "size_mb": l["size_mb"],
                "size_raw": l["size_raw"],
                "bar_pct": round((l["size_mb"] / max_mb) * 100),
                "cmd":     l["cmd"],
            }
            for i, l in enumerate(top5)
        ],
    }
    return json.dumps(result)
