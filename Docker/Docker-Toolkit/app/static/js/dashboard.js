// ── Tool definitions ──────────────────────────────────────────
const TOOL_ICONS = {
  lint: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>`,
  compose: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>`,
  image: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>`,
  image_size: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><polyline points="8 21 12 17 16 21"/><line x1="2" y1="20" x2="22" y2="20"/></svg>`,
  security: `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
};

const TOOLS = [
  {
    id: "lint",
    name: "Dockerfile Linter",
    badge: "6 checks",
    hint: "FROM, WORKDIR, USER, HEALTHCHECK…",
    instructions: `<strong>Expected Input</strong>
      Paste a complete <code>Dockerfile</code> — not a docker-compose file.
      <ul>
        <li>Must start with a <code>FROM</code> instruction</li>
        <li>One instruction per line (e.g. <code>RUN</code>, <code>COPY</code>, <code>EXPOSE</code>)</li>
        <li>Do not include image names alone — the full file is required</li>
      </ul>`,
    example: `FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nEXPOSE 5000\nCMD ["python", "app.py"]`,
  },
  {
    id: "compose",
    name: "Compose Validator",
    badge: "YAML",
    hint: "Services, volumes, healthchecks…",
    instructions: `<strong>Expected Input</strong>
      Paste a complete <code>docker-compose.yml</code> file.
      <ul>
        <li>Must start with <code>services:</code> at the top level</li>
        <li>Use proper YAML indentation (2 spaces)</li>
        <li>Do not paste a Dockerfile here</li>
      </ul>`,
    example: `services:\n  web:\n    build: .\n    ports:\n      - "5000:5000"\n    depends_on:\n      - redis\n  redis:\n    image: redis:7-alpine\n    volumes:\n      - redis-data:/data\nvolumes:\n  redis-data:`,
  },
  {
    id: "image",
    name: "Base Image Advisor",
    badge: "slim",
    hint: "Optimal tags, size estimates…",
    instructions: `<strong>Expected Input</strong>
      Enter a base image name — just the image reference, nothing else.
      <ul>
        <li>Format: <code>name:tag</code> e.g. <code>python:3.9</code></li>
        <li>Tag is optional — omitting it defaults to <code>latest</code></li>
        <li>Do not paste a full Dockerfile or YAML</li>
      </ul>`,
    example: `python:3.9`,
  },
  {
    id: "image_size",
    name: "Image Size Analyser",
    badge: "docker",
    hint: "Total size, heaviest layers…",
    instructions: `<strong>Expected Input</strong>
      Enter a Docker image name that exists locally or on a registry.
      <ul>
        <li>Format: <code>name:tag</code> e.g. <code>myapp:latest</code></li>
        <li>The image must be pullable — private images need prior <code>docker login</code></li>
        <li>One image per analysis — do not enter multiple names</li>
      </ul>`,
    example: `myapp:latest`,
  },
  {
    id: "security",
    name: "Security Scanner",
    badge: "CVE",
    hint: "Vulnerabilities by severity (Trivy)…",
    instructions: `<strong>Expected Input</strong>
      Enter a Docker image name to scan for CVEs using Trivy.
      <ul>
        <li>Format: <code>name:tag</code> e.g. <code>nginx:latest</code></li>
        <li>Public images are pulled automatically if not present locally</li>
        <li>One image per scan — scanning may take 10–30s for large images</li>
      </ul>`,
    example: `myapp:latest`,
  },
];

const TNAMES = {
  lint: "Dockerfile Linter",
  compose: "Compose Validator",
  image: "Base Image Advisor",
  image_size: "Image Size Analyser",
  security: "Security Scanner",
};

function lineStatus(l) {
  if (l.startsWith("[OK]")) return "ok";
  if (l.startsWith("[WARN]")) return "warn";
  if (l.startsWith("[ERR]")) return "err";
  if (l.startsWith("[FAIL]")) return "err";
  if (l.startsWith("[INFO]")) return "info";
  if (l.startsWith("[SCORE]")) return "score";
  return "";
}
// ── Build sidebar nav ─────────────────────────────────────────
let activeTool = null;
const toolNav = document.getElementById("tool-nav");
TOOLS.forEach((t) => {
  const el = document.createElement("div");
  el.className = "sb-item";
  el.dataset.id = t.id;
  el.innerHTML = `
    <span class="sb-icon">${TOOL_ICONS[t.id]}</span>
    <span class="sb-text"><span class="sb-name">${t.name}</span><span class="sb-badge">${t.badge}</span></span>
    <span class="tooltip">${t.name}</span>`;
  el.addEventListener("click", () => selectTool(t));
  toolNav.appendChild(el);
});

function selectTool(t) {
  activeTool = t;

  // Switch to Analyse tab
  document.querySelectorAll(".rp-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === "run");
  });
  document.querySelectorAll(".tab-pane").forEach((p) => {
    p.classList.toggle("active", p.id === "tab-run");
  });

  // Highlight sidebar item
  document
    .querySelectorAll(".sb-item")
    .forEach((el) => el.classList.toggle("active", el.dataset.id === t.id));

  // Update tool selector display
  const sel = document.getElementById("tool-sel");
  sel.innerHTML = TOOL_ICONS[t.id] + "&nbsp;&nbsp;" + t.name;
  sel.className = "tool-sel picked";

  // Show instructions
  const hint = document.getElementById("tool-instructions");
  if (t.instructions) {
    hint.innerHTML = t.instructions;
    hint.style.display = "block";
  } else {
    hint.style.display = "none";
  }

  // Update textarea placeholder
  document.getElementById("payload").placeholder =
    t.hint || "Paste your input here…";

  document.getElementById("run-btn").disabled = false;
}

// ── Sidebar toggle ────────────────────────────────────────────
const sidebar = document.getElementById("sidebar");
sidebar.classList.add("expanded");
document.getElementById("sb-toggle").addEventListener("click", () => {
  sidebar.classList.toggle("expanded");
});

// ── Example + char count ──────────────────────────────────────
const ta = document.getElementById("payload");
document.getElementById("ex-btn").addEventListener("click", () => {
  if (!activeTool) return;
  ta.value = activeTool.example;
  updateCC();
  ta.focus();
});
function updateCC() {
  document.getElementById("cc").textContent = ta.value.length + " chars";
}
ta.addEventListener("input", updateCC);

// ── Tabs ──────────────────────────────────────────────────────
document.querySelectorAll(".rp-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document
      .querySelectorAll(".rp-tab")
      .forEach((t) => t.classList.remove("active"));
    document
      .querySelectorAll(".tab-pane")
      .forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    document.getElementById("tab-" + tab.dataset.tab).classList.add("active");
  });
});

function switchTab(name) {
  document
    .querySelectorAll(".rp-tab")
    .forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document
    .querySelectorAll(".tab-pane")
    .forEach((p) => p.classList.toggle("active", p.id === "tab-" + name));
}

// ── Theme ─────────────────────────────────────────────────────
(function () {
  const btn = document.getElementById("theme-btn");
  let d = "dark";
  btn.addEventListener("click", () => {
    d = d === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", d);
    btn.textContent = d === "dark" ? "☀ Light" : "🌙 Dark";
  });
})();

// ── Toast ─────────────────────────────────────────────────────
function toast(icon, msg, sub) {
  const el = document.getElementById("toast");
  document.getElementById("t-icon").textContent = icon;
  document.getElementById("t-msg").textContent = msg;
  document.getElementById("t-sub").textContent = sub || "";
  el.classList.add("show");
  setTimeout(() => el.classList.remove("show"), 3000);
}

let scanCache = {};
const STATUS_DOT = { pending: "q", running: "p", passed: "c", failed: "f" };

function parseResult(raw) {
  return (raw || "")
    .split(" | ")
    .map((s) => s.trim())
    .filter(Boolean);
}

function selectScan(id) {
  document
    .querySelectorAll(".scan-card")
    .forEach((el) => el.classList.toggle("selected", el.dataset.id === id));
  showResult(id);

  // Switch to Report tab
  document.querySelectorAll(".rp-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === "result");
  });
  document.querySelectorAll(".tab-pane").forEach((p) => {
    p.classList.toggle("active", p.id === "tab-result");
  });
}

function renderSecurityScan(s, data) {
  const gradeColor = {
    CLEAN: "var(--green)",
    "LOW RISK": "var(--teal)",
    MODERATE: "var(--yellow)",
    "HIGH RISK": "var(--orange, #f97316)",
    "CRITICAL RISK": "var(--red)",
  };
  const col = gradeColor[data.grade] || "var(--muted)";

  const countBadges = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]
    .filter((sev) => data.counts[sev] > 0)
    .map((sev) => {
      const colors = {
        CRITICAL: "var(--red)",
        HIGH: "var(--orange, #f97316)",
        MEDIUM: "var(--yellow)",
        LOW: "var(--green)",
        UNKNOWN: "var(--muted)",
      };
      return `<span class="sec-badge" style="color:${colors[sev]};border-color:${colors[sev]}">
        ${sev} ${data.counts[sev]}</span>`;
    })
    .join("");

  const vulnRows = data.top_vulns.length
    ? data.top_vulns
        .map(
          (v) => `
      <div class="sec-vuln">
        <div class="sec-vuln-top">
          <span class="sec-sev sec-sev-${v.severity.toLowerCase()}">${v.icon}</span>
          <span class="sec-id">${v.id}</span>
          <span class="sec-pkg">${v.pkg} ${v.installed}</span>
          <span class="sec-fix ${v.fixed === "no fix available" ? "no-fix" : ""}">${v.fixed}</span>
        </div>
        ${v.title ? `<div class="sec-title">${v.title}</div>` : ""}
      </div>`,
        )
        .join("")
    : '<div class="sec-clean">[OK] No vulnerabilities found</div>';

  const note =
    data.top_vulns.length < data.total
      ? `<div class="is-note">Showing top ${data.top_vulns.length} of ${data.total} total vulnerabilities (CRITICAL + HIGH first).</div>`
      : "";

  document.getElementById("res-pane").innerHTML = `
    <div class="res-meta">
      <span class="res-tag">ID: <b>#${s.id}</b></span>
      <span class="res-tag">Status: <b style="color:${
        s.status === "passed"
          ? "var(--green)"
          : s.status === "failed"
            ? "var(--red)"
            : s.status === "running"
              ? "var(--blue)"
              : "var(--yellow)"
      }">${STATUS_LABEL[s.status] || s.status}</b></span>
      <span class="res-tag">At: <b>${s.submitted}</b></span>
      <span class="res-tag">Duration: <b>${s.duration !== "-" ? s.duration + "s" : "—"}</b></span>
    </div>
    <div class="is-header">
      <div class="is-image-name">${data.image}</div>
      <div class="is-total">
        <span class="is-total-val">${data.total} CVEs</span>
        <span class="is-grade" style="color:${col};border-color:${col}">${data.grade}</span>
      </div>
    </div>
    <div class="sec-counts">${countBadges || '<span style="color:var(--green)">No vulnerabilities</span>'}</div>
    <div class="is-section-lbl">TOP VULNERABILITIES</div>
    <div class="sec-vulns">${vulnRows}</div>
    ${note}
    <div class="res-line" data-s="score">
  <span class="res-tag-pill tag-score">SCORE</span>
  <span class="res-body">Security verdict: ${data.grade} — ${data.total} CVEs total</span>
  </div>`;
}

function renderImageSize(s, data) {
  const gradeColor = {
    LEAN: "var(--green)",
    OK: "var(--teal)",
    HEAVY: "var(--yellow)",
    BLOATED: "var(--red)",
  };
  const col = gradeColor[data.grade] || "var(--teal)";

  const layerRows = data.layers
    .map((l) => {
      const filled = Math.round((l.bar_pct / 100) * 20);
      const bar = "█".repeat(filled) + "░".repeat(20 - filled);
      const cmd = l.cmd.length > 72 ? l.cmd.slice(0, 69) + "…" : l.cmd;
      return `<div class="is-layer">
      <div class="is-layer-top">
        <span class="is-rank">#${l.rank}</span>
        <span class="is-bar" title="uncompressed">${bar}</span>
        <span class="is-size">${l.size_raw}</span>
      </div>
      <div class="is-cmd">${cmd}</div>
    </div>`;
    })
    .join("");

  document.getElementById("res-pane").innerHTML = `
    <div class="res-meta">
      <span class="res-tag">ID: <b>#${s.id}</b></span>
      <span class="res-tag">Status: <b style="color:${
        s.status === "passed"
          ? "var(--green)"
          : s.status === "failed"
            ? "var(--red)"
            : s.status === "running"
              ? "var(--blue)"
              : "var(--yellow)"
      }">${STATUS_LABEL[s.status] || s.status}</b></span>
      <span class="res-tag">At: <b>${s.submitted}</b></span>
      <span class="res-tag">Duration: <b>${s.duration !== "-" ? s.duration + "s" : "—"}</b></span>
    </div>
    <div class="is-header">
      <div class="is-image-name"> ${data.image}</div>
      <div class="is-total">
        <span class="is-total-val">${data.total_mb} MB</span>
        <span class="is-grade" style="color:${col};border-color:${col}">${data.grade}</span>
      </div>
    </div>
    <div class="is-section-lbl">
      LAYER BREAKDOWN
      <span class="is-layer-ct">${data.layer_count} non-zero layers · top ${data.layers.length} shown</span>
    </div>
    <div class="is-layers">${layerRows}</div>
    <div class="is-note">Bar widths and sizes are uncompressed weights from docker history.
Total compressed size reported by docker image inspect.</div>
    <div class="res-line" data-s="score">
  <span class="res-tag-pill tag-score">SCORE</span>
  <span class="res-body">Size verdict: ${data.grade} — ${data.total_mb} MB</span>`;
}


function showResult(id) {
  const s = scanCache[id];
  if (!s) return;

  // Structured JSON response (image_size / security_scan tools)
  try {
    const data = JSON.parse(s.result);
    if (data.__type === "image_size") {
      renderImageSize(s, data);
      return;
    }
    if (data.__type === "security_scan") {
      renderSecurityScan(s, data);
      return;
    }
  } catch (e) {}

  // Standard pipe-delimited response (all other tools)
  const lines = parseResult(s.result);
  document.getElementById("res-pane").innerHTML = `
  <div class="res-meta">
    <span class="res-tag">ID: <b>#${s.id}</b></span>
    <span class="res-tag">Status: <b style="color:${
      s.status === "passed"
        ? "var(--green)"
        : s.status === "failed"
          ? "var(--red)"
          : s.status === "running"
            ? "var(--blue)"
            : "var(--yellow)"
    }">${STATUS_LABEL[s.status] || s.status}</b></span>
    <span class="res-tag">At: <b>${s.submitted}</b></span>
    <span class="res-tag">Duration: <b>${s.duration !== "-" ? s.duration + "s" : "—"}</b></span>
  </div>
  <div>
    <div class="res-sect">Input</div>
    <div class="res-payload">${(s.payload || "").replace(/</g, "&lt;")}</div>
  </div>
    <div>
    <div class="res-sect">Analysis</div>
    <div style="display:flex;flex-direction:column;gap:6px;margin-top:4px">
      ${
        lines
          .map((l) => {
            if (l === "[GLOBAL]")
              return '<div class="res-group-header">Global</div>';
            if (l.startsWith("[SERVICE:") && l.endsWith("]"))
              return `<div class="res-group-header">Service: ${l.slice(9, -1).trim().toLowerCase()}</div>`;
            const st = lineStatus(l);
            return `<div class="res-line" data-s="${st}">
            ${st ? `<span class="res-tag-pill tag-${st}">${st.toUpperCase()}</span>` : ""}
            <span class="res-body">${l.replace(/^\[\w+\]\s*/, "")}</span>
          </div>`;
          })
          .join("") ||
        '<div class="res-line" data-s="ok"><span class="res-body">Analysis complete — no issues found.</span></div>'
      }
    </div>
  </div>`;
  
}


// ── Submit ────────────────────────────────────────────────────
document.getElementById("run-btn").addEventListener("click", async () => {
  if (!activeTool) return;
  const payload = ta.value.trim();
  if (!payload) {
    toast("", "Empty input", "Paste your config or image name first");
    return;
  }

  if (activeTool.id === "lint" && !payload.toUpperCase().includes("FROM")) {
    toast(
      "",
      "Invalid Dockerfile",
      "Must contain at least one FROM instruction",
    );
    return;
  }
  if (activeTool.id === "compose" && !payload.includes("services:")) {
    toast("", "Invalid Compose file", "Must start with a services: block");
    return;
  }
  if (
    ["image", "image_size", "security"].includes(activeTool.id) &&
    payload.includes("\n")
  ) {
    toast(
      "",
      "One image only",
      "Enter a single image name e.g. nginx:latest",
    );
    return;
  }

  const btn = document.getElementById("run-btn");
  btn.disabled = true;
  btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="animation:spin .6s linear infinite"><path d="M21 12a9 9 0 11-9-9"/></svg> Running…`;

  try {
    const fd = new FormData();
    fd.append("tool", TNAMES[activeTool.id]);
    fd.append("payload", payload);
    const res = await fetch("/analyse", { method: "POST", body: fd }).then(
      (r) => r.json(),
    );
    toast("", "Analysis queued", `scan #${res.scan_id} processing`);
    // WS will push the update automatically — just toast and wait
    pendingAutoSelect = res.scan_id;
  } catch (err) {
    toast("", "Submit failed", err.message);
  }
  btn.disabled = false;
  btn.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5,3 19,12 5,21"/></svg> Run Analysis`;
});

// ── Controls ──────────────────────────────────────────────────
document.getElementById("refresh-btn").addEventListener("click", async () => {
  const scans = await fetch("/scans").then((r) => r.json());
  scans.forEach((s) => (scanCache[s.id] = s));
  renderFeedFromCache();
  const st = await fetch("/stats").then((r) => r.json());
  applyStats(st);
});
document.getElementById("clear-btn").addEventListener("click", async () => {
  if (!confirm("Clear all scans and reset stats?")) return;
  await fetch("/clear", { method: "POST" });
  // feed_cleared WS event will reset UI
});

// ── WebSocket (socket.io) ─────────────────────────────────────
let pendingAutoSelect = null;
const STATUS_LABEL = {
  pending: "PENDING",
  running: "SCANNING",
  passed: "PASSED",
  failed: "FAILED",
};

function applyStats(s) {
  document.getElementById("vc").textContent = s.visits ?? "—";
  const fsDone = document.getElementById("fs-done");
  const fsFail = document.getElementById("fs-fail");
  const fsProc = document.getElementById("fs-proc");
  if (fsDone) fsDone.textContent = s.passed ?? 0;
  if (fsFail) fsFail.textContent = s.failed ?? 0;
  if (fsProc) fsProc.textContent = s.running ?? 0;

  const scannerList = document.getElementById("scanner-list");
  if (scannerList) {
    if (!s.scanners) {
      scannerList.innerHTML = `<div class="sc-item">
        <span style="font-size:.65rem;color:var(--faint)">—</span>
        <span class="sc-name" style="color:var(--faint)">No scanners</span>
      </div>`;
    } else {
      scannerList.innerHTML = Array.from(
        { length: s.scanners },
        (_, i) => `<div class="sc-item">
          <span class="sc-dot"></span>
          <span class="sc-name">scanner-${i + 1}</span>
          <span class="sc-tag">ready</span>
        </div>`,
      ).join("");
    }
  }
}

function upsertCard(s) {
  scanCache[s.id] = s;
  const feed = document.getElementById("feed");

  // Remove empty state if present
  const empty = feed.querySelector(".empty");
  if (empty) empty.remove();

  const dot = STATUS_DOT[s.status] || "q";
  const prev = (s.payload || "").split("\n")[0].slice(0, 34);
  const html = `<div class="scan-card" data-id="${s.id}" onclick="selectScan('${s.id}')">
    <div class="scan-row">
      <span class="scan-dot d-${dot}"></span>
      <div class="scan-info">
        <div class="scan-tool">${s.tool}</div>
        <div class="scan-meta">scan #${s.id} · ${prev}${prev.length >= 34 ? "…" : ""}</div>
      </div>
      <span class="scan-badge b-${dot}">${STATUS_LABEL[s.status] || s.status.toUpperCase()}</span>
      <span class="scan-time">${s.duration !== "-" ? s.duration + "s" : s.submitted}</span>
    </div>
  </div>`;

  const existing = feed.querySelector(`[data-id="${s.id}"]`);
  if (existing) {
    existing.outerHTML = html;
  } else {
    feed.insertAdjacentHTML("afterbegin", html);
  }

  // Update feed count
  const total = Object.keys(scanCache).length;
  document.getElementById("feed-ct").textContent =
    total + " scan" + (total !== 1 ? "s" : "");

  // pendingAutoSelect is cleared once the scan completes (tab switch handled by scan_update)
  if (
    pendingAutoSelect === s.id &&
    (s.status === "passed" || s.status === "failed")
  ) {
    pendingAutoSelect = null;
  }
}

function renderFeedFromCache() {
  const feed = document.getElementById("feed");
  const items = Object.values(scanCache).sort((a, b) =>
    (b.submitted || "").localeCompare(a.submitted || ""),
  );
  if (!items.length) {
    feed.innerHTML = `<div class="empty">
      <div class="empty-ico">🐳</div>
      <div class="empty-ttl">No analyses yet</div>
      <div class="empty-sub">Select a tool, paste your config<br>and hit Run Analysis.</div>
    </div>`;
    document.getElementById("feed-ct").textContent = "0 scans";
    return;
  }
  feed.innerHTML = items
    .slice(0, 100)
    .map((s) => {
      const dot = STATUS_DOT[s.status] || "q";
      const prev = (s.payload || "").split("\n")[0].slice(0, 34);
      return `<div class="scan-card" data-id="${s.id}" onclick="selectScan('${s.id}')">
      <div class="scan-row">
        <span class="scan-dot d-${dot}"></span>
        <div class="scan-info">
          <div class="scan-tool">${s.tool}</div>
          <div class="scan-meta">scan #${s.id} · ${prev}${prev.length >= 34 ? "…" : ""}</div>
        </div>
        <span class="scan-badge b-${dot}">${STATUS_LABEL[s.status] || s.status.toUpperCase()}</span>
        <span class="scan-time">${s.duration !== "-" ? s.duration + "s" : s.submitted}</span>
      </div>
    </div>`;
    })
    .join("");
  document.getElementById("feed-ct").textContent =
    items.length + " scan" + (items.length !== 1 ? "s" : "");
}

const socket = io();

socket.on("connect", async () => {
  console.log("WS connected:", socket.id);
  // Load initial state on connect/reconnect
  try {
    const [scans, st] = await Promise.all([
      fetch("/scans").then((r) => r.json()),
      fetch("/stats").then((r) => r.json()),
    ]);
    scanCache = {};
    scans.forEach((s) => (scanCache[s.id] = s));
    renderFeedFromCache();
    applyStats(st);
  } catch (e) {}
});

socket.on("disconnect", () => {
  console.warn("WS disconnected — will reconnect automatically");
});

socket.on("scan_update", (scan) => {
  upsertCard(scan);
  // Recount strip from cache
  const vals = Object.values(scanCache);
  const fsDone = document.getElementById("fs-done");
  const fsFail = document.getElementById("fs-fail");
  const fsProc = document.getElementById("fs-proc");
  if (fsDone)
    fsDone.textContent = vals.filter((s) => s.status === "passed").length;
  if (fsFail)
    fsFail.textContent = vals.filter((s) => s.status === "failed").length;
  if (fsProc)
    fsProc.textContent = vals.filter((s) => s.status === "running").length;

  // Auto-switch to Report tab only when scan is done AND result is ready
  if (
    (scan.status === "passed" || scan.status === "failed") &&
    scan.result !== undefined
  ) {
    selectScan(scan.id);
  }
});

socket.on("feed_cleared", () => {
  scanCache = {};
  renderFeedFromCache();
  const fsDone = document.getElementById("fs-done");
  const fsFail = document.getElementById("fs-fail");
  const fsProc = document.getElementById("fs-proc");
  if (fsDone) fsDone.textContent = 0;
  if (fsFail) fsFail.textContent = 0;
  if (fsProc) fsProc.textContent = 0;
  toast("", "Cleared", "All scans reset");
});
