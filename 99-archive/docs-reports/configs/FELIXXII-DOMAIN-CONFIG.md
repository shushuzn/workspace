# felixxii.xyz Domain Integration - Security Configuration

**Date:** 2026-03-14  
**Domain:** felixxii.xyz  
**Status:** 🟡 DNS Configuration Needed  
**Security:** Cloud First Architecture

---

## 🏗️ Architecture

```
PUBLIC INTERNET
       │
       ▼
┌──────────────────────────────────────┐
│   DNS Provider (Cloudflare)          │
│   Domain: felixxii.xyz               │
│   A: @ → 8.208.30.28                 │
│   CNAME: innovator → felixxii.xyz    │
│   CNAME: api → felixxii.xyz          │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   Cloud Server (8.208.30.28)         │
│   - nginx (80/443)                   │
│   - Dashboard (:8443/innovator)      │
│   - API (:3000)                      │
│   - SSL (Let's Encrypt)              │
└──────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│   Applications                       │
│   - https://felixxii.xyz/            │
│   - https://innovator.felixxii.xyz/  │
│   - https://api.felixxii.xyz/        │
└──────────────────────────────────────┘
```

---

## 🔒 Security Rules

### ✅ DO - Cloud Server
| Service | Domain | Deploy To |
|---------|--------|-----------|
| Main Site | felixxii.xyz | 8.208.30.28:80/443 |
| **Innovator Dashboard** | **innovator.felixxii.xyz** | **8.208.30.28:8443** |
| API | api.felixxii.xyz | 8.208.30.28:3000 |

### ❌ DON'T - Local Machine
- NO DNS point to local IP
- NO port forwarding locally
- NO SSL cert on local machine
- NO run services locally for public

---

## 📋 DNS Configuration

### Required DNS Records
| Type | Name | Value | TTL | Priority |
|------|------|-------|-----|----------|
| A | @ | 8.208.30.28 | 3600 | - |
| A | www | 8.208.30.28 | 3600 | - |
| **CNAME** | **innovator** | **felixxii.xyz** | **3600** | **-** |
| CNAME | api | felixxii.xyz | 3600 | - |

### Cloudflare Settings
- ✅ Proxy enabled (orange cloud) - DDoS protection
- ✅ SSL/TLS: Full (Strict)
- ✅ Auto HTTPS Rewrite: Enabled

---

## 🔧 Cloud Server Configuration

### SSL Certificate (Let's Encrypt)
```bash
ssh root@8.208.30.28
certbot --nginx -d felixxii.xyz -d www.felixxii.xyz -d innovator.felixxii.xyz -d api.felixxii.xyz
```

### nginx Reverse Proxy
```nginx
# Main Site
server {
    listen 443 ssl http2;
    server_name felixxii.xyz www.felixxii.xyz;
    ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    location / { proxy_pass http://127.0.0.1:3000; }
}

# Innovator Dashboard (integrated!)
server {
    listen 8443 ssl http2;
    server_name innovator.felixxii.xyz;
    ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    location / { 
        proxy_pass http://127.0.0.1:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# API Endpoint
server {
    listen 443 ssl http2;
    server_name api.felixxii.xyz;
    ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    location / { proxy_pass http://127.0.0.1:3000; }
}
```

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| DNS | 🔴 Not Configured | Need A/CNAME records |
| Cloud Server | ✅ Ready | 8.208.30.28 running |
| SSL Certificate | 🔴 Not Issued | Need Let's Encrypt |
| nginx Config | 🔴 Not Deployed | Need reverse proxy |
| **Innovator Dashboard** | **🟡 Integrated** | **innovator.felixxii.xyz** |
| API | 🟡 Planning | Deploy to cloud needed |

---

## 🎯 Key Learnings

- [SEC-014] Domain Cloud First - felixxii.xyz points to cloud server
- [SEC-015] DNS Security - Use Cloudflare proxy for DDoS protection
- [SEC-016] SSL Required - Let's Encrypt for all subdomains
- [SEC-017] No Local DNS - Never point domain to local IP
- [SEC-018] Subdomain Isolation - Separate subdomains for services
- **[SEC-019] Innovator Integrated** - **Dashboard on innovator.felixxii.xyz**

---

**Last Updated:** 2026-03-14 17:30  
**Owner:** OpenClaw Security + DevOps  
**Priority:** HIGH (Domain Integration)
