# Alibaba Cloud ECS Integration Guide

**Created:** 2026-03-14  
**Version:** 1.0  
**Purpose:** Connect Alibaba Cloud ECS server to OpenClaw workspace

---

## 🎯 Integration Scenarios

### Scenario 1: SSH Remote Access
- Access ECS from local workspace
- Run commands remotely
- Deploy services

### Scenario 2: File Synchronization
- Sync files between local and ECS
- Backup important data
- Share resources

### Scenario 3: Service Deployment
- Deploy OpenClaw Gateway on ECS
- Deploy Control UI on ECS
- Run collectors on ECS

### Scenario 4: Reverse Proxy
- Expose local services via ECS
- Public access to OpenClaw
- Domain binding

---

## 📋 Prerequisites

### ECS Information Required
| Item | Example | Where to Find |
|------|---------|---------------|
| Public IP | 47.100.xxx.xxx | ECS Console → Instances |
| Root Password | ******** | Set during creation |
| SSH Port | 22 | Security Group |
| Region | cn-shanghai | ECS Console |
| Instance ID | i-bp1xxxxxxxx | ECS Console |

### Security Group Rules
| Port | Protocol | Purpose |
|------|----------|---------|
| 22 | TCP | SSH Access |
| 18789 | TCP | OpenClaw Gateway |
| 80/443 | TCP | HTTP/HTTPS (optional) |

---

## 🔧 Setup Steps

### Step 1: Generate SSH Key (Optional but Recommended)

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "alibaba-cloud-ecs"

# Copy public key
type C:\Users\华为\.ssh\id_ed25519.pub
```

### Step 2: Configure SSH Config

Create `C:\Users\华为\.ssh\config`:
```ssh
Host aliyun-ecs
    HostName 47.100.xxx.xxx
    User root
    Port 22
    IdentityFile C:\Users\华为\.ssh\id_ed25519
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Step 3: Test SSH Connection

```bash
# Test connection
ssh aliyun-ecs

# Or with password
ssh root@47.100.xxx.xxx
```

### Step 4: Install Required Tools on ECS

```bash
# Update system
apt update && apt upgrade -y  # Ubuntu/Debian
# or
yum update -y  # CentOS/Alibaba Cloud Linux

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Install Python
apt install -y python3 python3-pip

# Install Git
apt install -y git

# Install OpenClaw
npm install -g openclaw
```

### Step 5: Configure OpenClaw on ECS

```bash
# Create .env file
nano ~/.openclaw/.env

# Add configuration
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_GATEWAY_HOST=0.0.0.0

# Start Gateway
openclaw gateway --port 18789
```

### Step 6: Configure Local OpenClaw

Edit `D:\OpenClaw\workspace\.env`:
```env
# Alibaba Cloud ECS Configuration
ALIYUN_ECS_HOST=47.100.xxx.xxx
ALIYUN_ECS_USER=root
ALIYUN_ECS_PORT=22
ALIYUN_ECS_SSH_KEY=C:/Users/华为/.ssh/id_ed25519

# Remote Gateway
ALIYUN_GATEWAY_URL=http://47.100.xxx.xxx:18789
```

---

## 📁 File Synchronization

### Option 1: rsync (Recommended)

```bash
# Install rsync on Windows (via Git Bash or WSL)

# Sync local → ECS
rsync -avz -e "ssh -p 22" /d/OpenClaw/workspace/ root@47.100.xxx.xxx:/root/openclaw-workspace/

# Sync ECS → local
rsync -avz -e "ssh -p 22" root@47.100.xxx.xxx:/root/openclaw-workspace/ /d/OpenClaw/workspace/
```

### Option 2: syncthing (Real-time Sync)

```bash
# Install syncthing on both local and ECS
# Configure sync folders
# Enable real-time synchronization
```

### Option 3: rclone (Cloud Storage)

```bash
# Install rclone
# Configure OSS (Alibaba Cloud Object Storage)
# Sync via OSS
```

---

## 🚀 Service Deployment

### Deploy OpenClaw Gateway on ECS

```bash
# Create systemd service
cat > /etc/systemd/system/openclaw-gateway.service << EOF
[Unit]
Description=OpenClaw Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/openclaw-workspace
ExecStart=/usr/bin/openclaw gateway --port 18789
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl enable openclaw-gateway
systemctl start openclaw-gateway
systemctl status openclaw-gateway
```

### Deploy Collectors on ECS

```bash
# Clone OpenClaw workspace
git clone <your-repo> /root/openclaw-workspace
cd /root/openclaw-workspace

# Install dependencies
npm install
pip install -r requirements.txt

# Run collectors
python 40-arxiv-collector/collector.py
```

---

## 🌐 Reverse Proxy Setup

### Option 1: Nginx Reverse Proxy

```bash
# Install Nginx
apt install -y nginx

# Configure Nginx
cat > /etc/nginx/sites-available/openclaw << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/openclaw /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Option 2: Cloudflare Tunnel

```bash
# Install cloudflared
# Configure tunnel to expose local Gateway
# No need to open ports on ECS
```

---

## 🔒 Security Best Practices

### 1. SSH Security
```bash
# Disable root password login
# Use SSH keys only
# Change default SSH port
# Install fail2ban
```

### 2. Firewall Configuration
```bash
# Configure security group
# Allow only necessary ports
# Use VPC private network when possible
```

### 3. Regular Updates
```bash
# Enable unattended-upgrades
# Monitor security advisories
# Regular system updates
```

---

## 📊 Monitoring & Maintenance

### System Monitoring
```bash
# Install htop
apt install -y htop

# Monitor resources
htop

# Check disk usage
df -h
```

### Log Management
```bash
# View OpenClaw logs
journalctl -u openclaw-gateway -f

# Rotate logs
logrotate
```

### Backup Strategy
```bash
# Create ECS snapshots
# Backup to OSS
# Regular backup schedule
```

---

## 🎯 Quick Start Commands

### Connect to ECS
```bash
ssh aliyun-ecs
```

### Sync Files
```bash
# Local → ECS
rsync -avz -e ssh /d/OpenClaw/workspace/ aliyun-ecs:/root/openclaw-workspace/

# ECS → Local
rsync -avz -e ssh aliyun-ecs:/root/openclaw-workspace/ /d/OpenClaw/workspace/
```

### Start Gateway on ECS
```bash
ssh aliyun-ecs "systemctl restart openclaw-gateway"
```

### Check Status
```bash
ssh aliyun-ecs "systemctl status openclaw-gateway"
```

---

## 📝 Configuration Files

### Local: `D:\OpenClaw\workspace\.env`
```env
# Alibaba Cloud ECS
ALIYUN_ECS_HOST=47.100.xxx.xxx
ALIYUN_ECS_USER=root
ALIYUN_ECS_PORT=22

# Remote Gateway
ALIYUN_GATEWAY_URL=http://47.100.xxx.xxx:18789

# Sync Configuration
SYNC_ENABLED=true
SYNC_INTERVAL=300
```

### ECS: `/root/.openclaw/.env`
```env
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_GATEWAY_HOST=0.0.0.0
```

### SSH Config: `C:\Users\华为\.ssh\config`
```ssh
Host aliyun-ecs
    HostName 47.100.xxx.xxx
    User root
    Port 22
    IdentityFile C:\Users\华为\.ssh\id_ed25519
```

---

## 🐛 Troubleshooting

### Issue 1: SSH Connection Failed
```bash
# Check security group
# Verify SSH port
# Test with verbose mode: ssh -v aliyun-ecs
```

### Issue 2: Gateway Not Accessible
```bash
# Check firewall
# Verify port is open: netstat -tlnp | grep 18789
# Check Gateway logs: journalctl -u openclaw-gateway
```

### Issue 3: Sync Failed
```bash
# Check disk space
# Verify permissions
# Test rsync manually
```

---

## 📈 Next Steps

1. **Configure SSH Key** - Generate and upload SSH key
2. **Test Connection** - Verify SSH access
3. **Install OpenClaw** - Deploy on ECS
4. **Configure Sync** - Set up file synchronization
5. **Start Gateway** - Run Gateway on ECS
6. **Test Integration** - Verify end-to-end connection

---

*Created:* 2026-03-14  
*Version:* 1.0  
*Status:* Ready for implementation  
*Next:* User to provide ECS details for configuration
