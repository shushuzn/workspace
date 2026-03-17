# Security Architecture - Cloud First

**Date:** 2026-03-14  
**Status:** ✅ Enforced  
**Principle:** Cloud Server First, No Local Exposure

---

## 🏗️ Architecture

```
PUBLIC INTERNET
       │
       ▼
┌──────────────────────────────────────┐
│   Cloud Server (OpenClaw-fipq)       │
│   IP: 8.208.30.28 (London)           │
│   - Web Console :8443                │
│   - API Services :3000               │
│   - Cron Jobs (internal)             │
└──────────────────────────────────────┘
       │
       │ SSH Only (Secure)
       ▼
┌──────────────────────────────────────┐
│   Local Machine (Development)        │
│   - SSH Client Only                  │
│   - NO Public Services               │
│   - NO Port Mapping                  │
│   - Dev on localhost only            │
└──────────────────────────────────────┘
```

---

## 🔒 Security Rules

### ✅ DO - Cloud Server
- Web Console → 8.208.30.28:8443
- API Endpoints → 8.208.30.28:3000
- Cron Jobs → 8.208.30.28 (internal)
- Database → 8.208.30.28 (internal)

### ❌ DON'T - Local Machine
- NO port mapping to public
- NO ngrok/frp tunneling
- NO UPnP port forwarding
- NO DMZ hosting
- NO public services locally

---

## 📋 Current Status

### Local Machine Audit (2026-03-14 17:05)
```
✅ No web server on 0.0.0.0
✅ No port 3000/8080/8443 exposed
✅ No tunneling software
✅ All dev services on 127.0.0.1 only
✅ System ports only (135, 445 - Windows)
```

### Cloud Server
- **IP:** 8.208.30.28 (London, UK)
- **SSH:** root@8.208.30.28
- **Status:** ⚠️ SSH timeout (network issue)

---

## 🎯 Key Learnings

- [SEC-001] Cloud First - All public services on cloud
- [SEC-002] No Local Exposure - Home network never exposed
- [SEC-003] SSH Only - Secure remote access only
- [SEC-006] Local Dev Secure - All services on localhost
- [SEC-007] Cloud First Confirmed - Public on 8.208.30.28
- [SEC-008] No Port Mapping - No local exposure
- [SEC-009] User Awareness - User identified security risk

---

**Last Review:** 2026-03-14 17:05  
**Next Review:** 2026-03-21 07:00  
**Owner:** OpenClaw Security
