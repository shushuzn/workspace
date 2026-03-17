# 🎭 Innovator Dashboard v3.0 - Deployment Guide

**Version:** 3.0 (Core Package)  
**Date:** 2026-03-15  
**Status:** ✅ Ready for Deployment

---

## 📦 Package Contents

| File | Size | Description |
|------|------|-------------|
| `dashboard-api-v3.py` | 17.5 KB | Backend API server (Python) |
| `innovator-dashboard-v3.html` | 28.9 KB | Frontend dashboard (HTML/CSS/JS) |
| `deploy-dashboard-v3.py` | 10.6 KB | Auto-deploy script (Python + paramiko) |
| `deploy-dashboard-v3.bat` | 3.3 KB | Auto-deploy script (Windows batch + SSH) |
| `dashboard-data/innovations.json` | 6.7 KB | Innovation database (20 entries) |
| `dashboard-data/persona-history.json` | 2.0 KB | 7-persona score history (7 days) |

**Total:** ~69 KB

---

## 🚀 Quick Deploy (Windows with SSH)

### Prerequisites
- SSH client installed (Git Bash or Windows OpenSSH)
- SSH access to 8.208.30.28 (root / 20051104sS)

### Steps
```bash
cd D:\OpenClaw\workspace
deploy-dashboard-v3.bat
```

**Enter password when prompted:** `20051104sS`

---

## 🚀 Manual Deploy (Alternative)

### Step 1: Connect to Server
```bash
ssh root@8.208.30.28
# Password: 20051104sS
```

### Step 2: Create Directory
```bash
mkdir -p /root/dashboard-v3
cd /root/dashboard-v3
```

### Step 3: Upload Files (from local machine)
```bash
# From Windows PowerShell
scp D:\OpenClaw\workspace\dashboard-api-v3.py root@8.208.30.28:/root/dashboard-v3/
scp D:\OpenClaw\workspace\innovator-dashboard-v3.html root@8.208.30.28:/root/dashboard-v3/
scp -r D:\OpenClaw\workspace\dashboard-data root@8.208.30.28:/root/dashboard-v3/
```

### Step 4: Install Dependencies
```bash
pip3 install psutil -q
```

### Step 5: Start Server
```bash
# Stop any existing server
pkill -f 'dashboard-api-v3.py' 2>/dev/null || true

# Start new server
nohup python3 dashboard-api-v3.py > dashboard.log 2>&1 &

# Verify it's running
lsof -i :8446 | grep LISTEN
```

### Step 6: Configure Firewall
```bash
ufw allow 8446/tcp
```

---

## 🌐 Access URLs

After deployment, access the dashboard at:

| Type | URL |
|------|-----|
| **Dashboard** | http://8.208.30.28:8446/ |
| **API** | http://8.208.30.28:8446/api/dashboard |
| **Health Check** | http://8.208.30.28:8446/api/health |

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | Session history (last 10) |
| GET | `/api/innovations` | Innovation database |
| GET | `/api/memory` | Memory distillation status |
| GET | `/api/git` | Git commit statistics |
| GET | `/api/health` | System health metrics |
| GET | `/api/personas` | 7-persona score history |
| GET | `/api/dashboard` | Full dashboard summary |
| POST | `/api/innovations` | Add new innovation |

### Example API Calls

```bash
# Get full dashboard data
curl http://8.208.30.28:8446/api/dashboard

# Get system health
curl http://8.208.30.28:8446/api/health

# Add new innovation
curl -X POST http://8.208.30.28:8446/api/innovations \
  -H "Content-Type: application/json" \
  -d '{"title":"New Feature","description":"Amazing feature","impact":"high"}'
```

---

## 🎯 Core Features (Phase 1)

### 1. 📝 Session History Tracker
- Last 10 sessions with ID, timestamp, duration
- Task count and innovation count per session
- Persona scores overview

### 2. 💡 Innovation Database
- 20 pre-loaded innovations (INNOVATOR-039 to 055)
- Filter by status (implemented/in_progress/pending)
- Filter by impact (high/medium/low)
- Add new innovations via API or UI (future)

### 3. 🧠 Memory Distillation Visualization
- Daily notes count
- MEMORY.md file size
- Weekly progress bar
- Recent notes list

### 4. 📊 Git Commit Tracker
- Today's commits
- This week's commits
- Total commits
- Recent commit history (last 10)
- File change statistics

### 5. ⚡ System Health Monitoring
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Health status (healthy/warning/critical)
- Cloud service status

### Bonus: 🎭 7-Persona Score Trends
- 7-day score history chart (Chart.js)
- All 7 personas tracked
- Average scores displayed

---

## 🔄 Auto-Refresh

Dashboard automatically refreshes every 5 minutes to show latest data.

Manual refresh button available in UI.

---

## 📁 Data Files

### innovations.json
```json
{
  "innovations": [...],
  "total": 20,
  "by_status": {"implemented": 20, "in_progress": 0, "pending": 0},
  "by_impact": {"high": 11, "medium": 7, "low": 4}
}
```

### persona-history.json
```json
{
  "history": [
    {"date": "2026-03-15", "scores": {...}, "average": 94.0}
  ],
  "averages": {...}
}
```

---

## 🛠️ Troubleshooting

### Server won't start
```bash
# Check if port is in use
lsof -i :8446

# Check logs
cat dashboard.log

# Run in foreground to see errors
python3 dashboard-api-v3.py
```

### Can't access from browser
```bash
# Check firewall
ufw status | grep 8446

# Open port if needed
ufw allow 8446/tcp

# Check server is listening
netstat -tlnp | grep 8446
```

### API returns errors
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip3 list | grep psutil

# Reinstall if needed
pip3 install psutil --upgrade
```

---

## 📈 Next Steps (Phase 2)

After Phase 1 is deployed and tested, consider adding:

- [ ] Automation task panel (Cron + HEARTBEAT)
- [ ] Decision log with LLM extraction
- [ ] 7-persona score trend analysis
- [ ] Feishu notification center
- [ ] File operation audit log

---

## 🎉 Success Criteria

Phase 1 is complete when:

- [x] All 5 core features implemented
- [x] API server runs without errors
- [x] Dashboard displays real-time data
- [x] Auto-refresh works (5 minutes)
- [x] Deployed to cloud server (8.208.30.28:8446)
- [ ] Accessible via browser ✅ **Pending deployment**

---

**Created by:** Claw 🐾  
**7-Persona System**  
**Session:** 2026-03-15
