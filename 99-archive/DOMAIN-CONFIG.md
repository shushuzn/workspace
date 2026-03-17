# 🌐 Innovator Domain Configuration

**Date:** 2026-03-14 17:45 HKT  
**Status:** ⏳ Pending DNS

---

## ✅ Current Status

| Domain | Status | IP |
|--------|--------|-----|
| **felixxii.xyz** | ✅ Resolved | 8.208.30.28 |
| **www.felixxii.xyz** | ✅ Resolved | 8.208.30.28 |
| **innovator.felixxii.xyz** | ❌ **Not configured** | - |

---

## 🔧 Required DNS Configuration

Login to **Cloudflare** and add:

### Option 1: CNAME (Recommended)

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | innovator | felixxii.xyz | ✅ Proxied (Orange cloud) |

### Option 2: A Record

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| A | innovator | 8.208.30.28 | ✅ Proxied (Orange cloud) |

---

## 📋 Steps

1. Login to Cloudflare: https://dash.cloudflare.com
2. Select domain: `felixxii.xyz`
3. Go to **DNS** → **Records**
4. Click **Add record**
5. Choose **CNAME** or **A**
6. Fill in details above
7. Ensure proxy is **Enabled** (orange cloud)
8. Click **Save**

---

## ⏱️ Propagation Time

- **Cloudflare:** Usually instant (1-2 minutes)
- **Global DNS:** 5-10 minutes
- **Maximum:** 24 hours (rare)

---

## 🧪 Verification

After adding DNS record, test:

```bash
# Check DNS
nslookup innovator.felixxii.xyz

# Test access
curl -k https://innovator.felixxii.xyz:8444

# Browser access
https://innovator.felixxii.xyz:8444
```

---

## 🔒 SSL Certificate

**Current:** Self-signed (valid 365 days)  
**Browser Warning:** Expected (click "Continue" or "Advanced" → "Proceed")

### Production SSL (Optional)

After DNS is configured:

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Request certificate
certbot --nginx -d innovator.felixxii.xyz

# Auto-renewal
certbot renew --dry-run
```

---

## 🌐 Access URLs

### Current (IP - Works Now)
- https://8.208.30.28:8444 ✅

### After DNS (Domain)
- https://innovator.felixxii.xyz:8444 ⏳

---

## 📊 Server Configuration

**nginx Config:** Already configured for domain  
**File:** `/etc/nginx/conf.d/innovator.conf`  
**server_name:** `innovator.felixxii.xyz`  
**Port:** 8444 (HTTPS)

No server changes needed - just add DNS!

---

**Ready to configure?** Open Cloudflare and add the DNS record above.
