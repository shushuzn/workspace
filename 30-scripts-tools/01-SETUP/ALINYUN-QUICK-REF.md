# Alibaba Cloud ECS - Quick Reference

**ECS IP:** `47.100.xxx.xxx` (Replace with your IP)  
**Region:** `cn-xxxx`  
**Created:** 2026-03-14

---

## 🔑 Quick Commands

### SSH Connection
```bash
# Connect to ECS
ssh aliyun-ecs

# Or with IP
ssh root@47.100.xxx.xxx

# With specific port
ssh -p 22 root@47.100.xxx.xxx
```

### File Sync
```bash
# Local → ECS
rsync -avz -e ssh /d/OpenClaw/workspace/ aliyun-ecs:/root/openclaw-workspace/

# ECS → Local
rsync -avz -e ssh aliyun-ecs:/root/openclaw-workspace/ /d/OpenClaw/workspace/

# Sync specific folder
rsync -avz -e ssh 13-memory-system/ aliyun-ecs:/root/openclaw-workspace/13-memory-system/
```

### Gateway Management
```bash
# Start Gateway on ECS
ssh aliyun-ecs "openclaw gateway --port 18789"

# Check Gateway status
ssh aliyun-ecs "systemctl status openclaw-gateway"

# Restart Gateway
ssh aliyun-ecs "systemctl restart openclaw-gateway"

# View Gateway logs
ssh aliyun-ecs "journalctl -u openclaw-gateway -f"
```

### Remote Commands
```bash
# Run command on ECS
ssh aliyun-ecs "uptime"
ssh aliyun-ecs "df -h"
ssh aliyun-ecs "htop"

# Copy file to ECS
scp file.txt aliyun-ecs:/root/

# Copy file from ECS
scp aliyun-ecs:/root/file.txt .
```

---

## 🔧 Configuration Files

| File | Path | Purpose |
|------|------|---------|
| SSH Config | `C:\Users\华为\.ssh\config` | SSH aliases |
| .env | `D:\OpenClaw\workspace\.env` | Workspace config |
| ECS .env | `/root/.openclaw/.env` | ECS Gateway config |

---

## 🌐 Security Group Rules

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| 22 | TCP | 0.0.0.0/0 | SSH |
| 18789 | TCP | 0.0.0.0/0 | Gateway |
| 80 | TCP | 0.0.0.0/0 | HTTP (optional) |
| 443 | TCP | 0.0.0.0/0 | HTTPS (optional) |

---

## 📊 Monitoring

### System Resources
```bash
# CPU & Memory
ssh aliyun-ecs "htop"

# Disk Usage
ssh aliyun-ecs "df -h"

# Network
ssh aliyun-ecs "iftop"

# Process List
ssh aliyun-ecs "ps aux"
```

### OpenClaw Status
```bash
# Gateway Status
ssh aliyun-ecs "systemctl status openclaw-gateway"

# Gateway Logs
ssh aliyun-ecs "journalctl -u openclaw-gateway -n 50"

# Check Port
ssh aliyun-ecs "netstat -tlnp | grep 18789"
```

---

## 🐛 Troubleshooting

### SSH Connection Failed
```bash
# Test connection
ssh -v aliyun-ecs

# Check security group
# Verify ECS is running
# Check SSH service: ssh aliyun-ecs "systemctl status sshd"
```

### Gateway Not Accessible
```bash
# Check if Gateway is running
ssh aliyun-ecs "systemctl status openclaw-gateway"

# Check port
ssh aliyun-ecs "netstat -tlnp | grep 18789"

# Check firewall
ssh aliyun-ecs "ufw status"
```

### Sync Failed
```bash
# Check disk space
ssh aliyun-ecs "df -h"

# Check permissions
ssh aliyun-ecs "ls -la /root/openclaw-workspace/"

# Test rsync
rsync -avz -e ssh --dry-run /d/OpenClaw/workspace/ aliyun-ecs:/root/openclaw-workspace/
```

---

## 📝 ECS Information

**Fill in your details:**

- **Public IP:** ____________________
- **Private IP:** ____________________
- **Instance ID:** ____________________
- **Region:** ____________________
- **OS:** ____________________
- **CPU:** ____________________
- **Memory:** ____________________
- **Disk:** ____________________
- **Created:** ____________________

---

*Last Updated:* 2026-03-14  
*Next Review:* After ECS setup completion
