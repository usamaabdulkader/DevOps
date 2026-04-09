"""
Docker Compose Validator — backed by `docker compose config` (official Docker validator).
Falls back to built-in yaml + rule checks if Docker CLI is not available.

Requires the Docker socket to be mounted in docker-compose.yml:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
"""
import shutil
import subprocess
import tempfile
import os
import yaml
from typing import Callable


RISKY_PORTS: dict[str, str] = {
    "6379":  "Redis",
    "5432":  "PostgreSQL",
    "3306":  "MySQL",
    "27017": "MongoDB",
    "9200":  "Elasticsearch",
    "9300":  "Elasticsearch transport",
    "2375":  "Docker daemon (unencrypted)",
    "2376":  "Docker daemon (TLS)",
}
HEALTHCHECK_EXEMPT: set[str] = {"nginx", "caddy", "traefik"}

CheckResult = tuple[str, int]

GRADES = [
    (9, "PRODUCTION READY"),
    (7, "GOOD"),
    (5, "REVIEW NEEDED"),
    (0, "NOT PRODUCTION READY"),
]


def _run_docker_compose_config(content: str) -> list[str]:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".yml", delete=False, prefix="compose_validate_"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["docker", "compose", "-f", tmp_path, "config", "--quiet"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    finally:
        os.unlink(tmp_path)

    lines = []
    if result.returncode == 0:
        lines.append("[OK] docker compose config: valid — no syntax errors")
    else:
        for err_line in result.stderr.strip().splitlines():
            err_line = err_line.strip()
            if err_line:
                lines.append(f"[ERR] {err_line}")
    return lines


def _check_restart(name: str, svc: dict) -> list[CheckResult]:
    if "restart" not in svc:
        return [("[WARN] No restart policy — add restart: unless-stopped", 1)]
    return [(f"[OK] Restart policy: {svc['restart']}", 0)]


def _check_healthcheck(name: str, svc: dict) -> list[CheckResult]:
    if name in HEALTHCHECK_EXEMPT:
        return []
    if "healthcheck" in svc:
        return [("[OK] Healthcheck defined", 0)]
    return [("[WARN] No healthcheck defined", 1)]


def _check_risky_ports(name: str, svc: dict) -> list[CheckResult]:
    issues = []
    for p in svc.get("ports", []):
        host_port = str(p).split(":")[0].strip().strip("'\"")
        if host_port in RISKY_PORTS:
            issues.append((
                f"[WARN] {RISKY_PORTS[host_port]} port {host_port} exposed to host",
                1,
            ))
    return issues


def _check_depends_on(name: str, svc: dict) -> list[CheckResult]:
    results = []
    if isinstance(svc.get("depends_on"), dict):
        for dep, cond in svc["depends_on"].items():
            if isinstance(cond, dict) and cond.get("condition") == "service_healthy":
                results.append((f"[OK] depends_on '{dep}': service_healthy condition set", 0))
            else:
                results.append((
                    f"[WARN] depends_on '{dep}': no health condition — may start before ready",
                    1,
                ))
    return results


def _check_env(name: str, svc: dict) -> list[CheckResult]:
    if "env_file" in svc or "environment" in svc:
        return [("[OK] Environment variables configured", 0)]
    return []


def _check_image_or_build(name: str, svc: dict) -> list[CheckResult]:
    if "image" not in svc and "build" not in svc:
        return [("[WARN] Neither image nor build defined", 1)]
    return []


SERVICE_CHECKS: list[Callable] = [
    _check_image_or_build,
    _check_restart,
    _check_healthcheck,
    _check_risky_ports,
    _check_depends_on,
    _check_env,
]


def _run_service_checks(data: dict) -> tuple[list[str], int]:
    services = data.get("services", {})
    results = []
    score = 10

    results.append("[GLOBAL]")
    results.append(f"[OK] {len(services)} service(s) found: {', '.join(services.keys())}")

    volumes = data.get("volumes", {})
    if volumes:
        results.append(f"[OK] Named volumes: {', '.join(volumes.keys())}")
    else:
        results.append("[WARN] No named volumes — data won't persist across restarts")
        score -= 1

    networks = data.get("networks", {})
    if networks:
        results.append(f"[OK] Custom networks: {', '.join(networks.keys())}")

    for name, svc in services.items():
        if not svc:
            continue

        svc_lines = []
        svc_score = 0

        for check_fn in SERVICE_CHECKS:
            for message, penalty in check_fn(name, svc):
                svc_lines.append(message)
                svc_score += penalty

        results.append(f"[SERVICE: {name.upper()}]")
        results.extend(svc_lines)
        score -= svc_score

    return results, max(0, score)


def validate_compose(content: str) -> str:
    results = []
    score = 10

    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise RuntimeError(f"[FAIL] Invalid YAML — {str(e)[:120]}")

    if not isinstance(data, dict) or "services" not in data:
        raise RuntimeError("[FAIL] No 'services' key found — is this a valid docker-compose.yml?")

    docker_bin = shutil.which("docker")
    cli_available = False

    if docker_bin:
        probe = subprocess.run(
            ["docker", "compose", "version"],
            capture_output=True, text=True, timeout=5
        )
        cli_available = probe.returncode == 0

    if cli_available:
        try:
            cli_lines = _run_docker_compose_config(content)
            if any(l.startswith("[ERR]") for l in cli_lines):  # ← fix here
                results.append("[INFO] docker compose config → structure & syntax")
                results.extend(cli_lines)
                results.append("[SCORE] 0/10 — INVALID (fix syntax errors before re-running)")
                return " | ".join(results)
            results.append("[INFO] docker compose config → structure & syntax")
            results.extend(cli_lines)
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            results.append(f"[WARN] docker CLI error ({e}) — skipping syntax validation")
    else:
        results.append(
            "[WARN] docker compose config: skipped — docker CLI not found"
        )

    

    results.append("[INFO] built-in analyser → best practices & security")
    svc_results, score = _run_service_checks(data)
    results.extend(svc_results)

    grade = next(label for threshold, label in GRADES if score >= threshold)
    results.append(f"[SCORE] {score}/10 — {grade}")
    return " | ".join(results)