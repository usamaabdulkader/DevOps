# ⚓ Dockyard

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/version-1.0.0-green.svg)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)

**Dockyard** is a lightweight, efficient container inspection and management tool designed to give developers deep visibility into their containerized environments. It is a containerized web application that provides a suite of tools for analyzing, validating, and securing Docker artifacts. It features an interactive, responsive dashboard with a real-time analysis feed powered by WebSockets.


## Prerequisites
Before you begin, ensure you have the following installed on your local machine or server:

- [Docker](https://docs.docker.com/get-docker/) v20+
- [Docker Compose](https://docs.docker.com/compose/) v2+

---

### 🛠️ Tools Included

1. **Dockerfile Linter**: Validates `Dockerfile`s using `hadolint` (industry standard) and built-in best practices. It checks for issues like missing `FROM` instructions, running as root, and missing healthchecks.
2. **Compose Validator**: Analyzes `docker-compose.yml` files using the official `docker compose config` and built-in rules to ensure proper healthchecks, restart policies, and to warn against risky exposed ports.
3. **Base Image Advisor**: Connects to container registries (like Docker Hub and AWS Public ECR) to fetch metadata on base images, checking for stale tags and recommending optimal, slim variants.
4. **Image Size Analyser**: Inspects built local images via the Docker CLI to provide a breakdown of the total size and the heaviest uncompressed layers.
5. **Security Scanner**: Uses `Trivy` to scan Docker images for vulnerabilities (CVEs), categorizing them by severity (Critical, High, Medium, Low) and providing an overall security grade.


## Architecture

```
Browser
   │
   ▼
Nginx (port 5000)
   │
   ▼
Web (Flask + Gunicorn + Socket.IO)
   │                    │
   ▼                    ▼
Redis (queue)      WebSocket push
   │
   ▼
Scanner Worker (Python)
   │
   └── tools/
       ├── compose.py     ← Validates docker-compose files
       ├── image.py       ← Inspects Docker images
       ├── image_size.py  ← Checks image bloat
       ├── linter.py      ← Lints Dockerfile syntax
       └── security.py    ← Runs security checks
```

**Services (Docker Compose):**

| Service   | Description                                              |
|-----------|----------------------------------------------------------|
| `web`     | Flask app served via Gunicorn + eventlet                 |
| `scanner` | Background worker that processes scan jobs from Redis    |
| `redis`   | Queue (BRPOP/LPUSH) + pub/sub for real-time WS events    |
| `nginx`   | Reverse proxy — exposes everything on port 5000          |

---

## UI Features

- **Real-time Dashboard** — scan cards update live via Socket.IO
- **Scan History** — results stored in Redis, retrievable via `/scans`
- **Live Stats** — visit count, pending/running/passed/failed counters

---

## Project Structure

```
Dockyard/
├── app/
│   ├── app.py              # Flask app — routes, WebSocket, Redis pub/sub listener
│   ├── scanner.py          # Worker — dequeues and runs scans
│   ├── redis_keys.py       # Centralised Redis key constants
│   ├── requirements.txt    # Python dependencies
│   ├── dockerfile          # Image definition for web + scanner
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   │   └── index.html
│   └── tools/
│       ├── __init__.py
│       ├── compose.py
│       ├── image.py
│       ├── image_size.py
│       ├── linter.py
│       └── security.py
├── redis/
│   └── Dockerfile          # Custom Redis image
├── nginx/
│   └── nginx.conf          # Reverse proxy config
└── docker-compose.yml
```

---



## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/usamaabdulkader/DevOps.git
cd DevOps/Docker/Dockyard
```

### 2. Build and start all services

```bash
docker compose up --build
```

### 3. Open the app

Visit [http://localhost:5000](http://localhost:5000) in your browser.

### 4. Stop the services

```bash
docker compose down
```

To also remove persisted Redis data:

```bash
docker compose down -v
```

---

## Environment Variables

| Variable     | Default                  | Description                        |
|--------------|--------------------------|------------------------------------|
| `REDIS_HOST` | `redis`                  | Redis service hostname             |
| `REDIS_PORT` | `6379`                   | Redis port                         |
| `SECRET_KEY` | `dockyard-secret`        | Flask session secret key           |

These are set in `docker-compose.yml` and can be overridden with a `.env` file.

---

## API Endpoints

| Method | Endpoint   | Description                              |
|--------|------------|------------------------------------------|
| GET    | `/`        | Main dashboard UI                        |
| POST   | `/analyse` | Submit a scan (`tool` + `payload` fields)|
| GET    | `/scans`   | Retrieve all scan results                |
| GET    | `/stats`   | Get live scan statistics                 |
| POST   | `/clear`   | Clear scan queue and reset counters      |

---

## How It Works

1. User submits a config/payload via the UI and selects a tool.
2. The web service pushes a scan job onto the Redis queue and emits a `pending` card to the browser via WebSocket.
3. The scanner worker picks up the job (`BRPOP`), runs the selected tool, and updates the result in Redis.
4. The result is published to the `scan_events` Redis channel.
5. The web service's pub/sub listener picks up the event and pushes a `scan_update` to all connected WebSocket clients — the UI card updates in real time.

---

## Scan Result Grades

The scanner derives a pass/fail status from each tool's output:

- **Passed** — no `[ERR]` / `[FAIL]` tokens, or JSON grade is not HIGH/CRITICAL RISK
- **Failed** — contains `[ERR]` / `[FAIL]`, or grade is `HIGH RISK`, `CRITICAL RISK`, or `BLOATED`

---

## Dependencies

```
flask
flask-socketio>=5.3
eventlet>=0.35
redis
requests
pyyaml
gunicorn
```

---

## Notes

- The scanner mounts the Docker socket (`/var/run/docker.sock`) in read-only mode to run `docker compose config` for Compose validation.
- Redis data is persisted via a named Docker volume (`redis-data`).
- Nginx runs on `alpine` and proxies all traffic to the Gunicorn/eventlet web service.