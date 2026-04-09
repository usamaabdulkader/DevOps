"""
Dockerfile Linter — backed by hadolint (industry standard).
Falls back to built-in rules if hadolint is not installed.
"""
import json
import shutil
import subprocess
from dataclasses import dataclass


HADOLINT_SEVERITY_MAP = {
    "error":   "[ERR]",
    "warning": "[WARN]",
    "info":    "[INFO]",
    "style":   "[INFO]",
}


def _run_hadolint(content: str) -> list[str]:
    result = subprocess.run(
        ["hadolint", "--format", "json", "-"],
        input=content, capture_output=True, text=True, timeout=15,
    )
    try:
        findings = json.loads(result.stdout or "[]")
    except json.JSONDecodeError:
        findings = []

    if not findings:
        return ["[OK] hadolint: no issues found"]

    lines = []
    for f in sorted(findings, key=lambda x: x.get("line", 0)):
        tag  = HADOLINT_SEVERITY_MAP.get(f.get("level", ""), "[INFO]")
        code = f.get("code", "")
        line = f.get("line", "?")
        msg  = f.get("message", "")
        lines.append(f"{tag} Line {line} [{code}]: {msg}")
    return lines


@dataclass
class Rule:
    id: str
    description: str
    penalty: int
    check: object


def _check_from(lines):
    issues, found = [], False
    for i, s in enumerate(lines, 1):
        if s.startswith("FROM"):
            found = True
            parts = s.split()
            image = parts[1] if len(parts) > 1 else ""
            if ":latest" in image or (image and ":" not in image):
                issues.append(f"[ERR] Line {i}: Avoid :latest — pin to a specific tag (e.g. python:3.12-slim)")
            else:
                issues.append(f"[OK] Line {i}: Specific base image tag — good")
    if not found:
        issues.append("[ERR] No FROM instruction found")
    return issues


def _check_workdir(lines):
    return ["[OK] WORKDIR is defined"] if any(s.startswith("WORKDIR") for s in lines) \
        else ["[WARN] No WORKDIR set — files land in / by default"]


def _check_user(lines):
    return ["[OK] Non-root USER defined"] if any(s.startswith("USER") for s in lines) \
        else ["[WARN] No USER instruction — container runs as root (security risk)"]


def _check_healthcheck(lines):
    return ["[OK] HEALTHCHECK defined"] if any(s.startswith("HEALTHCHECK") for s in lines) \
        else ["[WARN] No HEALTHCHECK — Docker cannot detect app failures"]


def _check_run_consolidation(lines):
    count = sum(1 for s in lines if s.startswith("RUN"))
    return [f"[WARN] {count} RUN commands — chain with && to reduce image layers"] if count > 2 else []


def _check_nocache(lines):
    return ["[OK] --no-cache-dir used in pip install"] if any("--no-cache-dir" in s for s in lines) else []


def _check_copy_all(lines):
    return [
        f"[WARN] Line {i}: COPY . . copies everything — add a .dockerignore file"
        for i, s in enumerate(lines, 1)
        if s.startswith("COPY . .") or s == "COPY . /app"
    ]


RULES = [
    Rule("from",        "FROM with pinned tag",           3, _check_from),
    Rule("workdir",     "WORKDIR defined",                1, _check_workdir),
    Rule("user",        "Non-root USER",                  1, _check_user),
    Rule("healthcheck", "HEALTHCHECK present",            1, _check_healthcheck),
    Rule("run_layers",  "RUN commands consolidated",      1, _check_run_consolidation),
    Rule("nocache",     "--no-cache-dir in pip",          0, _check_nocache),
    Rule("copy_all",    "COPY . . without .dockerignore", 1, _check_copy_all),
]

# Descending order — next() stops at first threshold score meets
GRADES = [(9, "EXCELLENT"), (7, "GOOD"), (5, "FAIR"), (0, "NEEDS WORK")]


def _fallback_lint(lines):
    results, score = [], 10
    for rule in RULES:
        for finding in rule.check(lines):
            results.append(finding)
            if finding.startswith(("[ERR]", "[WARN]")):
                score -= rule.penalty
    return results, max(0, score)


def lint_dockerfile(content: str) -> str:
    lines = [l.strip() for l in content.strip().splitlines()]

    if shutil.which("hadolint"):
        try:
            findings = _run_hadolint(content)
            errors   = sum(1 for f in findings if f.startswith("[ERR]"))
            warnings = sum(1 for f in findings if f.startswith("[WARN]"))
            score    = max(0, 10 - errors * 2 - warnings)
            grade    = next(label for threshold, label in GRADES if score >= threshold)
            findings.insert(0, "[INFO] Linted with hadolint")
            findings.append(f"[SCORE] {score}/10 — {grade}")
            return " | ".join(findings)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    # Built-in fallback
    results, score = _fallback_lint(lines)
    grade = next(label for threshold, label in GRADES if score >= threshold)
    results.insert(0, "[INFO] Linted with built-in rules (install hadolint for deeper analysis)")
    results.append(f"[SCORE] {score}/10 — {grade}")
    return " | ".join(results)
