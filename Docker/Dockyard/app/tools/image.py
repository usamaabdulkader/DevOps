"""
Base Image Advisor — multi-registry aware.

Supported:
- Docker Hub official images (python, node, redis…)
- Docker Hub namespaced images (bitnami/redis, grafana/grafana…)
- AWS Public ECR (public.ecr.aws/namespace/image)

Unsupported (noted in output, tag-pinning advice still shown):
- AWS Private ECR (*.dkr.ecr.*.amazonaws.com/…)
- GitHub Container Registry (ghcr.io/…)
- Google Container Registry (gcr.io/…, us-docker.pkg.dev/…)
- Quay.io (quay.io/…)
- Any other private/unknown registry
"""
import re
import time
import urllib.request
import urllib.error
import json
from datetime import datetime

# ── API endpoints ──────────────────────────────────────────────────
# Fetch 100 tags (was 25) so all active major versions are visible
DOCKERHUB_TAGS = "https://hub.docker.com/v2/repositories/{repo}/tags?page_size=100&ordering=last_updated"
DOCKERHUB_INFO = "https://hub.docker.com/v2/repositories/{repo}/"
ECR_PUBLIC_TAGS = "https://api.us-east-1.gallery.ecr.aws/v1/tags?registryAliasName={alias}&repositoryName={repo}&maxResults=100"
ECR_PUBLIC_INFO = "https://api.us-east-1.gallery.ecr.aws/v1/repos?registryAliasName={alias}&repositoryName={repo}"

TIMEOUT   = 8
CACHE_TTL = 300  # seconds — Docker Hub tag data is stable for 5 min

# Simple in-memory TTL cache: { url: (timestamp, data) }
# Shared across all scans for the lifetime of the scanner process.
_cache: dict = {}


def _fetch_cached(url: str, headers: dict | None = None) -> dict:
    """Fetch URL with a TTL cache. Bypasses network on cache hit."""
    now = time.monotonic()
    if url in _cache:
        ts, data = _cache[url]
        if now - ts < CACHE_TTL:
            return data
    data = _fetch(url, headers)
    _cache[url] = (now, data)
    return data

PREFERRED_SUFFIXES = ["-slim", "-alpine", "-bookworm-slim", "-jammy", "-noble"]
EXCLUDED_TAGS = {"latest", "edge", "stable", "mainline", "alpine", "slim"}
STABLE_RE = re.compile(r'^[0-9]+(\.[0-9]+)*(-[a-z0-9]+)*$')

# ── Registry detection ─────────────────────────────────────────────

UNSUPPORTED_REGISTRIES = {
    "ghcr.io":           "GitHub Container Registry",
    "gcr.io":            "Google Container Registry",
    "us-docker.pkg.dev": "Google Artifact Registry",
    "eu-docker.pkg.dev": "Google Artifact Registry",
    "quay.io":           "Quay.io",
    "registry.k8s.io":   "Kubernetes Registry",
    "mcr.microsoft.com": "Microsoft Container Registry",
}

PRIVATE_ECR_RE = re.compile(r'^\d{12}\.dkr\.ecr\.[a-z0-9-]+\.amazonaws\.com')
PUBLIC_ECR_RE  = re.compile(r'^public\.ecr\.aws/([a-z0-9_-]+)/([a-z0-9_.-]+)')


def _detect_registry(raw: str) -> tuple[str, dict]:
    image = raw.split(":")[0]

    if PRIVATE_ECR_RE.match(image):
        host = image.split("/")[0]
        name = "/".join(image.split("/")[1:])
        return "ecr_private", {"host": host, "name": name}

    m = PUBLIC_ECR_RE.match(image)
    if m:
        return "ecr_public", {"alias": m.group(1), "repo": m.group(2)}

    for host, label in UNSUPPORTED_REGISTRIES.items():
        if image.startswith(host + "/"):
            return "unsupported", {"host": host, "label": label, "image": image}

    if "/" in image and "." not in image.split("/")[0]:
        parts = image.split("/", 1)
        return "dockerhub_namespaced", {"namespace": parts[0], "name": parts[1]}

    return "dockerhub_official", {"name": image}


# ── HTTP helpers ───────────────────────────────────────────────────

def _fetch(url: str, headers: dict | None = None) -> dict:
    req = urllib.request.Request(url, headers={"Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def _fmt_size(full_size: int) -> str:
    if not full_size:
        return "size unknown"
    return f"~{round(full_size / 1_048_576)}MB"


def _fmt_date(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y")
    except (ValueError, AttributeError):
        return iso or "unknown"


# ── Version-aware sorting ──────────────────────────────────────────

def _version_tuple(tag_name: str) -> tuple:
    """Extract leading numeric version as a sortable tuple, e.g. '9.3-slim' → (9, 3)."""
    m = re.match(r'^(\d+(?:\.\d+)*)', tag_name)
    if not m:
        return (0,)
    return tuple(int(x) for x in m.group(1).split("."))


def _pick_best(tags: list[dict], name_key: str = "name") -> dict | None:
    """
    Pick the best tag by:
      1. Filter out excluded / unstable tags
      2. Sort all candidates by version number descending (highest major first)
      3. Within the highest major version group, prefer slim > alpine > bare
    """
    candidates = [
        t for t in tags
        if t.get(name_key) not in EXCLUDED_TAGS
        and STABLE_RE.match(t.get(name_key, ""))
    ]
    if not candidates:
        return None

    # Sort by version tuple descending — pure arithmetic, zero hardcoding
    candidates.sort(key=lambda t: _version_tuple(t[name_key]), reverse=True)

    # Find the highest major version present
    top_major = _version_tuple(candidates[0][name_key])[0]

    # Restrict to tags sharing that major version
    top_candidates = [
        t for t in candidates
        if _version_tuple(t[name_key])[0] == top_major
    ]

    # Within the top major group prefer slim variants
    for suffix in PREFERRED_SUFFIXES:
        for t in top_candidates:
            if t[name_key].endswith(suffix):
                return t

    # Fall back to highest version bare tag
    return top_candidates[0]


# ── Registry-specific handlers ─────────────────────────────────────

def _advise_dockerhub(repo: str, current_tag: str, image_label: str) -> list[str]:
    results = []
    try:
        meta  = _fetch_cached(DOCKERHUB_INFO.format(repo=repo))
        stars = meta.get("star_count", "?")
        pulls = meta.get("pull_count", "?")
        results.append("[INFO] Docker Hub API → live tag data")
        if isinstance(stars, int): stars = f"{stars:,}"
        if isinstance(pulls, int): pulls = f"{pulls:,}"
        results.append(f"[INFO] {image_label} · {stars} stars · {pulls} pulls")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(
                f"[WARN] '{image_label}' not found on Docker Hub. "
                "For private images prefix with your namespace (e.g. myorg/myapp)."
            )
        results.append("[INFO] Docker Hub API → live tag data")
        results.append(f"[WARN] Could not fetch image metadata (HTTP {e.code})")

    tag_data = _fetch_cached(DOCKERHUB_TAGS.format(repo=repo))
    tags = tag_data.get("results", [])

    if not tags:
        results.append("[WARN] No tags returned from Docker Hub")
        return results

    # Check current tag status — search all 100 fetched tags
    current_meta = next((t for t in tags if t["name"] == current_tag), None)

    if current_tag == "latest":
        results.append("[ERR] :latest is unpinned — produces non-reproducible builds")
    elif current_meta:
        pushed = _fmt_date(current_meta.get("tag_last_pushed", ""))
        size   = _fmt_size(current_meta.get("full_size", 0))
        results.append(f"[OK] Tag '{current_tag}' exists · {size} · pushed {pushed}")
    else:
        results.append(f"[WARN] Tag '{current_tag}' not found in latest 100 — may be outdated or misspelled")

    # Recommend best tag using version-aware logic
    best = _pick_best(tags)
    if best:
        rec_size   = _fmt_size(best.get("full_size", 0))
        rec_pushed = _fmt_date(best.get("tag_last_pushed", ""))
        if best["name"] == current_tag:
            results.append(f"[OK] '{current_tag}' is already the recommended tag")
        else:
            results.append(
                f"[OK] Recommended: {image_label}:{best['name']} · {rec_size} · pushed {rec_pushed}"
            )

    # Show up to 5 recent stable tags sorted by version desc
    stable_sorted = sorted(
        [t["name"] for t in tags
         if t.get("name") not in EXCLUDED_TAGS and STABLE_RE.match(t.get("name", ""))],
        key=_version_tuple,
        reverse=True,
    )[:5]
    if stable_sorted:
        results.append(f"[OK] Recent stable tags: {' · '.join(stable_sorted)}")

    return results


def _advise_ecr_public(alias: str, repo: str, current_tag: str) -> list[str]:
    results = ["[INFO] AWS Public ECR API → live tag data"]
    try:
        tag_data = _fetch_cached(ECR_PUBLIC_TAGS.format(alias=alias, repo=repo))
        tags = [
            {"name": t.get("imageTag", ""), "full_size": 0,
             "tag_last_pushed": t.get("createdAt", "")}
            for t in tag_data.get("imageTags", []) if t.get("imageTag")
        ]

        if not tags:
            results.append("[WARN] No tags returned from ECR Public")
            return results

        current_meta = next((t for t in tags if t["name"] == current_tag), None)
        if current_tag == "latest":
            results.append("[ERR] :latest is unpinned — produces non-reproducible builds")
        elif current_meta:
            pushed = _fmt_date(current_meta.get("tag_last_pushed", ""))
            results.append(f"[OK] Tag '{current_tag}' exists on ECR Public · pushed {pushed}")
        else:
            results.append(f"[WARN] Tag '{current_tag}' not found in latest results")

        best = _pick_best(tags)
        if best and best["name"] != current_tag:
            pushed = _fmt_date(best.get("tag_last_pushed", ""))
            results.append(f"[INFO] Recommended: public.ecr.aws/{alias}/{repo}:{best['name']} · pushed {pushed}")
        elif best:
            results.append(f"[OK] '{current_tag}' is already the recommended tag")

        stable_sorted = sorted(
            [t["name"] for t in tags
             if t["name"] not in EXCLUDED_TAGS and STABLE_RE.match(t["name"])],
            key=_version_tuple,
            reverse=True,
        )[:5]
        if stable_sorted:
            results.append(f"[INFO] Recent stable tags: {' · '.join(stable_sorted)}")

    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        results.append(f"[WARN] ECR Public API unreachable — {e}")

    return results


def _advise_unsupported(label: str, host: str, raw: str, current_tag: str) -> list[str]:
    results = [
        f"[WARN] {label} ({host}) → registry API not supported",
        "ℹ️ Tag-pinning advice only — no live data available",
    ]
    if current_tag == "latest":
        results.append("[ERR] :latest is unpinned — produces non-reproducible builds")
    else:
        results.append(f"[OK] Tag '{current_tag}' is pinned — good practice")
    return results


def _advise_ecr_private(host: str, name: str, current_tag: str) -> list[str]:
    results = [
        f"[WARN] AWS Private ECR ({host}) → requires AWS credentials, cannot query",
        "ℹ[INFO] Tag-pinning advice only — authenticate with ECR for full inspection",
    ]
    if current_tag == "latest":
        results.append("[ERR] :latest is unpinned — produces non-reproducible builds")
    else:
        results.append(f"[OK] Tag '{current_tag}' is pinned — good practice")
    return results


# ── Public entry point ─────────────────────────────────────────────

def advise_base_image(content: str) -> str:
    raw         = content.strip()
    current_tag = raw.split(":")[-1] if ":" in raw else "latest"

    registry, parsed = _detect_registry(raw)
    results = [f"[INFO] Base: {raw}"]

    if registry == "dockerhub_official":
        results += _advise_dockerhub(
            repo=f"library/{parsed['name']}",
            current_tag=current_tag,
            image_label=parsed["name"],
        )
    elif registry == "dockerhub_namespaced":
        results += _advise_dockerhub(
            repo=f"{parsed['namespace']}/{parsed['name']}",
            current_tag=current_tag,
            image_label=f"{parsed['namespace']}/{parsed['name']}",
        )
    elif registry == "ecr_public":
        results += _advise_ecr_public(
            alias=parsed["alias"],
            repo=parsed["repo"],
            current_tag=current_tag,
        )
    elif registry == "ecr_private":
        results += _advise_ecr_private(
            host=parsed["host"],
            name=parsed["name"],
            current_tag=current_tag,
        )
    elif registry == "unsupported":
        results += _advise_unsupported(
            label=parsed["label"],
            host=parsed["host"],
            raw=raw,
            current_tag=current_tag,
        )

    return " | ".join(results)
