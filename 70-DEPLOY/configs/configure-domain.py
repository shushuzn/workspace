#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("CONFIGURING INNOVATOR DOMAIN ACCESS")
print("=" * 60)

# Updated nginx config with domain
nginx_config = """server {
    listen 8444 ssl http2;
    server_name innovator.felixxii.xyz;
    
    # SSL certificates
    ssl_certificate     /etc/nginx/ssl/innovator.crt;
    ssl_certificate_key /etc/nginx/ssl/innovator.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    root /var/www/innovator;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Cache static assets
    location ~* \\.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Access log
    access_log /var/log/nginx/innovator.access.log;
    error_log /var/log/nginx/innovator.error.log;
}
"""

print("\n[1/3] Checking current nginx config...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/conf.d/innovator.conf | grep server_name")
print(stdout.read().decode())

print("\n[2/3] Config already has domain name - checking DNS...")
stdin, stdout, stderr = ssh.exec_command("ping -c 1 innovator.felixxii.xyz 2>&1 | head -2")
result = stdout.read().decode()
print(result)

print("\n[3/3] Testing local access with domain...")
stdin, stdout, stderr = ssh.exec_command("curl -k -I https://localhost:8444 2>&1 | head -3")
print(stdout.read().decode())

print("\n" + "=" * 60)
print("DNS CONFIGURATION NEEDED")
print("=" * 60)
print("\nAdd this record in Cloudflare:")
print("\nType: CNAME")
print("Name: innovator")
print("Content: felixxii.xyz")
print("Proxy: Enabled (orange cloud)")
print("\nOr use A record:")
print("Type: A")
print("Name: innovator")
print("Content: 8.208.30.28")
print("Proxy: Enabled")

ssh.close()
