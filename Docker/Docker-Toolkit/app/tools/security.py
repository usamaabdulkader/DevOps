"""
Security Scanner — backed by Trivy (industry standard CVE scanner).
Scans a local image for vulnerabilities and returns structured JSON.

Requires:
- Trivy installed in the container
- /var/run/docker.sock mounted read-only
"""
import json
import shutil
import subprocess

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]
# Replace SEVERITY_ICON dict
SEVERITY_ICON = {
    "CRITICAL": "CRIT",
    "HIGH":     "HIGH",
    "MEDIUM":   "MED",
    "LOW":      "LOW",
    "UNKNOWN":  "UNK",
}

GRADE_THRESHOLDS = [
    (lambda c: c["CRITICAL"] == 0 and c["HIGH"] == 0, "CLEAN"),
    (lambda c: c["CRITICAL"] == 0 and c["HIGH"] <= 3, "LOW RISK"),
    (lambda c: c["CRITICAL"] == 0, "MODERATE"),
    (lambda c: c["CRITICAL"] <= 3, "HIGH RISK"),
    (lambda c: True, "CRITICAL RISK"),
]


def _grade(counts: dict) -> str:
    for fn, label in GRADE_THRESHOLDS:
        if fn(counts):
            return label
    return "CRITICAL RISK"


def scan_image(content: str) -> str:
    image = content.strip()
    if not image:
        raise RuntimeError("Provide an image name, e.g. myapp:latest")

    if not shutil.which("trivy"):
        raise RuntimeError("Trivy not found — install it in the app image and rebuild")

    proc = subprocess.run(
        [
            "trivy", "image",
            "--format", "json",
            "--scanners", "vuln",
            "--quiet",
            "--no-progress",
            image,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    err = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()

    # ── Detect image-not-found before anything else ──────────────
    if not stdout and proc.returncode != 0:
        if (
            "No such image" in err
            or "not found" in err.lower()
            or "UNAUTHORIZED" in err
            or "does not exist" in err.lower()
            or not err  # trivy exited non-zero with no output at all
        ):
            raise RuntimeError(
                f"Image '{image}' not found — it may not exist locally or the tag is invalid. "
                f"Check hub.docker.com for valid tags (e.g. mysql:7 does not exist, use mysql:8 or mysql:5.7)."
            )
        raise RuntimeError(f"Trivy error (exit {proc.returncode}): {err[:300]}")

    # ── Strip any leading non-JSON noise ─────────────────────────
    json_start = stdout.find("{")
    if json_start > 0:
        stdout = stdout[json_start:]

    if not stdout:
        raise RuntimeError(
            f"Trivy returned no output for '{image}' — "
            f"ensure the image exists locally and Docker socket is mounted."
        )

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"Trivy output could not be parsed for '{image}'. "
            f"Raw output (first 200 chars): {stdout[:200]!r}"
        )

    seen = set()
    all_vulns = []
    results = data.get("Results") or data.get("results") or []
    for target in results:
        vulns = target.get("Vulnerabilities") or target.get("vulnerabilities") or []
        for v in vulns:
            key = v.get("VulnerabilityID", "")
            if key in seen:
                continue
            seen.add(key)
            all_vulns.append({
                "id": v.get("VulnerabilityID", ""),
                "severity": v.get("Severity", "UNKNOWN").upper(),
                "pkg": v.get("PkgName", ""),
                "installed": v.get("InstalledVersion", ""),
                "fixed": v.get("FixedVersion", "") or "no fix available",
                "title": (v.get("Title") or v.get("Description") or "")[:80],
            })

    counts = {s: 0 for s in SEVERITY_ORDER}
    for v in all_vulns:
        counts[v["severity"]] = counts.get(v["severity"], 0) + 1

    grade = _grade(counts)
    priority = sorted(
        all_vulns,
        key=lambda v: SEVERITY_ORDER.index(v["severity"]) if v["severity"] in SEVERITY_ORDER else 99,
    )[:10]

    result = {
        "__type": "security_scan",
        "image": image,
        "grade": grade,
        "total": len(all_vulns),
        "counts": counts,
        "top_vulns": [
            {
                "id": v["id"],
                "severity": v["severity"],
                "icon": SEVERITY_ICON.get(v["severity"], "UNK"),
                "pkg": v["pkg"],
                "installed": v["installed"],
                "fixed": v["fixed"],
                "title": v["title"],
            }
            for v in priority
        ],
    }

    return json.dumps(result)
