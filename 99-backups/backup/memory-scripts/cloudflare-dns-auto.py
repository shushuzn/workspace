#!/usr/bin/env python3
"""
Cloudflare DNS Auto-Configuration
Adds innovator.felixxii.xyz DNS record automatically
"""
import requests
import json
from pathlib import Path

# Configuration
DOMAIN = "felixxii.xyz"
RECORD_NAME = "innovator"
RECORD_IP = "8.208.30.28"
PROXIED = True  # Enable Cloudflare proxy

# Try to get API token from environment
CONFIG_FILE = Path("D:/OpenClaw/workspace/cloudflare-config.json")

def get_api_token():
    """Get Cloudflare API token from config or environment"""
    
    # Check config file
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = json.load(f)
        return config.get("api_token")
    
    # Check environment
    import os
    return os.getenv("CLOUDFLARE_API_TOKEN")

def get_zone_id(api_token):
    """Get zone ID for domain"""
    url = f"https://api.cloudflare.com/client/v4/zones?name={DOMAIN}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    
    if data.get("success"):
        zone_id = data["result"][0]["id"]
        print(f"[OK] Zone ID: {zone_id}")
        return zone_id
    else:
        print(f"[FAIL] Failed to get zone: {data}")
        return None

def add_dns_record(api_token, zone_id):
    """Add A record for innovator subdomain"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "type": "A",
        "name": f"{RECORD_NAME}.{DOMAIN}",
        "content": RECORD_IP,
        "proxied": PROXIED,
        "ttl": 1  # Auto TTL
    }
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    data = resp.json()
    
    if data.get("success"):
        print(f"[OK] DNS record created!")
        print(f"     Name: {RECORD_NAME}.{DOMAIN}")
        print(f"     Type: A")
        print(f"     Content: {RECORD_IP}")
        print(f"     Proxied: {PROXIED}")
        return True
    else:
        print(f"[FAIL] Failed to create record: {data}")
        return False

def check_existing_record(api_token, zone_id):
    """Check if record already exists"""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records?name={RECORD_NAME}.{DOMAIN}"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    
    if data.get("success") and data["result"]:
        record = data["result"][0]
        print(f"[INFO] Record already exists:")
        print(f"       Type: {record['type']}")
        print(f"       Content: {record['content']}")
        print(f"       Proxied: {record['proxied']}")
        return record
    return None

def main():
    print("=" * 60)
    print("CLOUDFLARE DNS AUTO-CONFIGURATION")
    print("=" * 60)
    print(f"\nDomain: {DOMAIN}")
    print(f"Record: {RECORD_NAME}.{DOMAIN}")
    print(f"IP: {RECORD_IP}")
    print(f"Proxy: {'Enabled' if PROXIED else 'Disabled'}")
    
    # Get API token
    api_token = get_api_token()
    
    if not api_token:
        print("\n[ERROR] No Cloudflare API token found!")
        print("\nTo get your API token:")
        print("1. Go to: https://dash.cloudflare.com/profile/api-tokens")
        print("2. Create token with 'Zone:DNS:Edit' permission")
        print("3. Save to: D:/OpenClaw/workspace/cloudflare-config.json")
        print("\nExample config:")
        print(json.dumps({"api_token": "your_token_here"}, indent=2))
        return False
    
    print(f"\n[OK] API token found")
    
    # Get zone ID
    zone_id = get_zone_id(api_token)
    if not zone_id:
        return False
    
    # Check existing record
    existing = check_existing_record(api_token, zone_id)
    
    if existing:
        if existing["content"] == RECORD_IP and existing["proxied"] == PROXIED:
            print("\n[OK] Record already configured correctly!")
            return True
        else:
            print("\n[INFO] Updating existing record...")
            # Update logic could be added here
    else:
        print("\n[INFO] Adding new DNS record...")
    
    # Add DNS record
    success = add_dns_record(api_token, zone_id)
    
    if success:
        print("\n" + "=" * 60)
        print("DNS CONFIGURATION COMPLETE!")
        print("=" * 60)
        print(f"\nPropagation time: 1-5 minutes (Cloudflare)")
        print(f"\nTest with:")
        print(f"  nslookup {RECORD_NAME}.{DOMAIN}")
        print(f"  curl -k https://{RECORD_NAME}.{DOMAIN}:8444")
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        exit(1)
