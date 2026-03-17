#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("UPDATING: Main Domain Direct Access")
print("=" * 60)

# Updated config - serve innovator content directly on main domain
nginx_config = """# Main domain - HTTPS - Direct access to Innovator
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name felixxii.xyz www.felixxii.xyz;
    
    # SSL certificates
    ssl_certificate     /etc/nginx/ssl/felixxii.crt;
    ssl_certificate_key /etc/nginx/ssl/felixxii.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Serve Innovator Dashboard directly
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
    
    # Logs
    access_log /var/log/nginx/felixxii.access.log;
    error_log /var/log/nginx/felixxii.error.log;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name felixxii.xyz www.felixxii.xyz;
    
    location / {
        return 301 https://$host:443$request_uri;
    }
}
"""

print("\n[1/3] Updating nginx configuration...")
stdin, stdout, stderr = ssh.exec_command("tee /etc/nginx/conf.d/felixxii-main.conf > /dev/null")
stdin.write(nginx_config)
stdin.close()
print("[OK] Configuration updated")

print("\n[2/3] Testing and reloading...")
stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
output = stdout.read().decode() + stderr.read().decode()
print(output)

print("\n[3/3] Testing access...")
stdin, stdout, stderr = ssh.exec_command("curl -k -I https://localhost:443 2>&1")
print(stdout.read().decode())

print("\n" + "=" * 60)
print("COMPLETE!")
print("=" * 60)
print("\nAccess URLs:")
print("  ✅ https://felixxii.xyz (Innovator Dashboard)")
print("  ✅ https://www.felixxii.xyz (Innovator Dashboard)")
print("  ✅ https://felixxii.xyz:8444 (Direct port)")
print("  ✅ https://8.208.30.28:8444 (Direct IP)")

ssh.close()
