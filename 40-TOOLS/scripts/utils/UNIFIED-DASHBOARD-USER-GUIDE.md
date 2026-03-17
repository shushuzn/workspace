# Unified Dashboard v1.0 - User Guide

**Date:** 2026-03-17 20:20  
**Version:** 1.0  
**Status:** ✅ **READY TO USE**

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start Dashboard
```bash
# Double-click this file:
start-unified-dashboard.bat

# OR run from command line:
cd D:\OpenClaw\workspace
python 30-scripts-tools\unified_dashboard.py
```

### Step 2: Open Browser
Browser should open automatically to:
```
http://localhost:8500
```

If not, manually open the URL above.

### Step 3: Monitor!
- Check **Overview** tab for quick status
- Switch to **System Health** for detailed metrics
- Review **Memory System** for MEMORY.md stats
- Track **Innovation** for project progress
- See **All Dashboards** for complete inventory

---

## 📊 Dashboard Tabs Explained

### Tab 1: Overview 📊
**Purpose:** Quick system-wide summary

**Metrics Shown:**
- System Health Score (0-100)
- MEMORY.md File Size (KB)
- Innovation Score (/100)
- Total Python Tools

**Visual:** Doughnut chart showing resource usage

**When to Use:** Daily check-in, quick status assessment

---

### Tab 2: System Health 💻
**Purpose:** Detailed system resource monitoring

**Metrics Shown:**
- CPU Usage (%)
- Memory Usage (%)
- Disk Usage (%)
- Network Traffic (Upload/Download MB)
- Health Score with status badges

**Table:** Detailed breakdown with status (Healthy/Warning/Critical)

**When to Use:** Troubleshooting performance issues, resource planning

---

### Tab 3: Memory System 🧠
**Purpose:** MEMORY.md and search system monitoring

**Metrics Shown:**
- File Size (KB)
- Total Lines
- Encoding (UTF-8 verification)
- Search Sections Indexed
- Quality Score (/100)
- Last Updated Timestamp

**When to Use:** After memory operations, compression checks

---

### Tab 4: Innovation 💡
**Purpose:** Track innovation and development progress

**Metrics Shown:**
- Innovation Score (/100)
- Total Python Tools
- Test Coverage (%)
- Active Projects
- Last Commit Date

**Visual:** Bar chart comparing Innovation/Test/Memory quality

**When to Use:** Sprint reviews, innovation tracking

---

### Tab 5: All Dashboards 📈
**Purpose:** Complete inventory of all 7 dashboards

**Information:**
- Dashboard Name
- Port Number
- Script Location
- Features List
- Status (Available/Offline)

**Dashboards Listed:**
1. v4.1-Persona (8448) - Default
2. v4.0 (8447) - Legacy
3. v3.0 (8446) - Legacy
4. Static (8080) - Lightweight
5. Innovator (HTML)
6. Research (HTML)
7. KG Lessons (HTML)

**When to Use:** Finding specific dashboard, checking availability

---

## 🔧 Configuration

### Change Refresh Interval
Edit `30-scripts-tools/unified_dashboard.py`:
```python
# Line 17
REFRESH_INTERVAL = 10  # Change to desired seconds (5-60)
```

### Change Port
Edit `30-scripts-tools/unified_dashboard.py`:
```python
# Line 16
PORT = 8500  # Change to desired port
```

### Add New Metrics
1. Add data collection method in `UnifiedDashboardData` class
2. Add HTML elements in `HTML_TEMPLATE`
3. Update JavaScript `updateDashboard()` function

---

## 🎨 UI Features

### Auto-Refresh
- **Interval:** 10 seconds (configurable)
- **Countdown:** Shows seconds until next refresh
- **Manual:** Click "🔄 Refresh" button for immediate update

### Status Badges
- **✅ Healthy** (Green) - Score ≥ 80
- **⚠️ Warning** (Yellow) - Score 60-79
- **❌ Critical** (Red) - Score < 60

### Charts
- **Doughnut Chart:** System resources overview
- **Bar Chart:** Quality & innovation comparison
- **Interactive:** Click legend to toggle datasets

---

## 🐛 Troubleshooting

### Dashboard Won't Start
**Problem:** Error when running `start-unified-dashboard.bat`

**Solutions:**
1. Check Python installation:
   ```bash
   python --version
   ```
   Should show Python 3.8+

2. Install psutil:
   ```bash
   pip install psutil
   ```

3. Check if port 8500 is in use:
   ```bash
   netstat -ano | findstr :8500
   ```
   If in use, kill process or change port in config

### Browser Doesn't Open
**Problem:** Dashboard starts but browser doesn't open

**Solution:** Manually open:
```
http://localhost:8500
```

### Charts Not Loading
**Problem:** Dashboard loads but charts are blank

**Solutions:**
1. Check internet connection (Chart.js loads from CDN)
2. Open browser console (F12) for errors
3. Refresh page (Ctrl+R)

### Metrics Not Updating
**Problem:** Values stuck or showing "--"

**Solutions:**
1. Click "🔄 Refresh" button
2. Check browser console for errors
3. Restart dashboard (Ctrl+C, then run again)

### High CPU Usage
**Problem:** Dashboard causing high CPU

**Solutions:**
1. Increase refresh interval (edit `REFRESH_INTERVAL`)
2. Close unused browser tabs
3. Check system health tab for actual CPU usage

---

## 📊 API Endpoints

### Get All Data
```
GET http://localhost:8500/api/data
```
**Response:** JSON with all metrics

**Example:**
```json
{
  "timestamp": "2026-03-17T20:15:30",
  "system_health": {
    "cpu_percent": 14.6,
    "memory_percent": 71.5,
    "disk_percent": 68.2,
    "health_score": 95
  },
  "memory_system": {
    "file_size_kb": 11.1,
    "lines": 363,
    "quality_score": 100
  },
  "innovation": {
    "innovation_score": 119.5,
    "total_tools": 273
  }
}
```

### Health Check
```
GET http://localhost:8500/api/health
```
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-17T20:15:30"
}
```

---

## 🔮 Future Enhancements

### Phase 2 (Week 2)
- WebSocket real-time push (replace polling)
- Historical data storage (SQLite)
- Alert system (visual/audio)
- Export to CSV/PDF

### Phase 3 (Week 3)
- Mobile responsive design
- Dark mode toggle
- Multi-language support (EN/ZH)
- Feishu notification integration

### Phase 4 (Week 4)
- AI-powered insights (LLM)
- Predictive alerts
- Custom dashboard views
- Plugin system

---

## 📈 Usage Examples

### Example 1: Daily Check-in
1. Run `start-unified-dashboard.bat`
2. Check **Overview** tab (5 seconds)
3. Verify health score > 90
4. Close dashboard or leave running

### Example 2: Troubleshooting
1. Notice system slowdown
2. Open **System Health** tab
3. Check CPU/Memory/Disk usage
4. Identify bottleneck (e.g., CPU at 95%)
5. Take action (close processes, restart services)

### Example 3: Innovation Review
1. Open **Innovation** tab
2. Check innovation score trend
3. Review tool count growth
4. Verify test coverage > 80%
5. Plan next innovation sprint

### Example 4: Memory Audit
1. Open **Memory System** tab
2. Check file size (should be ~10 KB)
3. Verify quality score = 100
4. Check last updated timestamp
5. Run memory compression if size > 15 KB

---

## 🎯 Best Practices

### DO ✅
- Run dashboard daily for monitoring
- Keep refresh interval at 10s (balanced)
- Check health score weekly
- Export metrics before major changes
- Use tabbed navigation for efficiency

### DON'T ❌
- Set refresh interval < 5s (excessive CPU)
- Ignore critical status badges
- Run multiple instances (port conflict)
- Leave running overnight (unnecessary)
- Modify code without backup

---

## 📞 Support

### Documentation
- `UNIFIED-DASHBOARD-REPORT.md` - Implementation details
- `WORKSPACE-DASHBOARD-OVERVIEW.md` - All dashboards comparison
- `HEARTBEAT.md` - Integration with heartbeat system

### Logs
Dashboard logs to console. Check for:
- Startup messages
- API request logs
- Error messages

### Common Issues
| Issue | Solution |
|-------|----------|
| Port in use | Change PORT in config |
| psutil missing | `pip install psutil` |
| Charts blank | Check internet (CDN) |
| Metrics stale | Click Refresh button |

---

## 🎉 Success Metrics

**Dashboard is working if:**
- ✅ Browser opens to http://localhost:8500
- ✅ 5 tabs visible and clickable
- ✅ Metrics show actual values (not "--")
- ✅ Auto-refresh countdown working
- ✅ Charts render correctly
- ✅ Status badges show correct color

---

## 📋 Checklist

### First-Time Setup
- [ ] Python 3.8+ installed
- [ ] psutil installed (`pip install psutil`)
- [ ] `start-unified-dashboard.bat` accessible
- [ ] Port 8500 available
- [ ] Browser works

### Daily Use
- [ ] Run `start-unified-dashboard.bat`
- [ ] Check Overview tab
- [ ] Verify health score > 90
- [ ] Review any warnings
- [ ] Close or minimize dashboard

### Weekly Review
- [ ] Check innovation score trend
- [ ] Review memory system stats
- [ ] Verify test coverage
- [ ] Export metrics (future feature)
- [ ] Plan improvements

---

## 🎯 Conclusion

**Unified Dashboard v1.0** is your one-stop shop for workspace monitoring!

**Quick Start:**
```bash
start-unified-dashboard.bat
```

**Access:** http://localhost:8500

**Features:** 5 tabs, 20+ metrics, auto-refresh, charts, status badges

**Innovation:** 120.0/100 🎯

**Status:** ✅ **PRODUCTION READY**

---

**Guide Version:** 1.0  
**Last Updated:** 2026-03-17 20:20  
**Author:** Claw (AI Agent)  
**Next Review:** 2026-03-24 (Week 2 enhancements)
