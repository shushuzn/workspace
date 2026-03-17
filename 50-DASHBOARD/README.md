# Dashboard - Configuration & Usage

**Location:** `50-DASHBOARD/`

**Last Updated:** 2026-03-18 00:45

---

## Default Dashboard (v4.1-Persona)

**Start Command:** `start-dashboard.bat`

**Port:** 8448

**API Endpoint:** http://localhost:8448/api/personas

---

## Features

### 7-Persona System

| Persona | Role |
|---------|------|
| Planner | Task decomposition & planning |
| Executor | Task execution & monitoring |
| Critic | Quality review & feedback |
| Learner | Knowledge acquisition & integration |
| Coordinator | Multi-agent orchestration |
| Innovator | Creative problem solving |
| Metacognition | Self-reflection & improvement |

### Technical Features

- **Async I/O** - Non-blocking operations
- **WebSocket** - Real-time communication
- **Redis Queue** - Task buffering
- **REST API** - HTTP endpoints for integration

---

## Quick Start

```powershell
# Start dashboard
cd 50-DASHBOARD
.\start-dashboard.bat

# Access UI
http://localhost:8448

# API test
curl http://localhost:8448/api/personas
```

---

## Configuration

**Config File:** `50-DASHBOARD/config.json`

**Environment Variables:**
```bash
DASHBOARD_PORT=8448
REDIS_HOST=localhost
REDIS_PORT=6379
LLM_HOST=localhost:11434
LLM_MODEL=qwen2.5:1.5b
```

---

## Monitoring

**Health Check:**
```bash
curl http://localhost:8448/api/health
```

**Metrics:**
- Request count
- Response time
- Active personas
- Queue depth

---

## Troubleshooting

### Dashboard won't start
```powershell
# Check port availability
netstat -ano | findstr :8448

# Kill process if needed
taskkill /F /PID <PID>

# Restart
.\start-dashboard.bat
```

### API not responding
```powershell
# Check Redis
redis-cli ping

# Check logs
Get-Content logs\dashboard.log -Tail 50
```

---

## Development

**Directory Structure:**
```
50-DASHBOARD/
├── api/          # API endpoints
├── data/         # Dashboard data
├── web/          # Web UI (HTML/CSS/JS)
├── config.json   # Configuration
└── start-dashboard.bat  # Launcher
```

---

## History

- **v4.1-Persona** (2026-03-17) - Current default, 7 personas
- **v4.0** - WebSocket + Redis integration
- **v3.0** - Async I/O support
- **v2.0** - REST API
- **v1.0** - Basic web UI

---

**See Also:** `70-DEPLOY/dashboard/` for deployment configurations
