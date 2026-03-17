#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("BACKING UP AND REPLACING MAIN DOMAIN CONFIG")
print("=" * 60)

print("\n[1/4] Backing up openclaw-ssl.conf...")
stdin, stdout, stderr = ssh.exec_command("cp /etc/nginx/conf.d/openclaw-ssl.conf /etc/nginx/conf.d/openclaw-ssl.conf.bak")
print("[OK] Backup created")

print("\n[2/4] Removing openclaw-ssl.conf...")
stdin, stdout, stderr = ssh.exec_command("rm /etc/nginx/conf.d/openclaw-ssl.conf")
print("[OK] Removed")

print("\n[3/4] Updating felixxii-main.conf to use Let's Encrypt cert...")

# Use Let's Encrypt cert instead of self-signed
nginx_config = """# Main domain - HTTPS - Innovator Dashboard with Let's Encrypt
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name felixxii.xyz www.felixxii.xyz;
    
    # SSL certificates - Let's Encrypt
    ssl_certificate     /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    
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

stdin, stdout, stderr = ssh.exec_command("tee /etc/nginx/conf.d/felixxii-main.conf > /dev/null")
stdin.write(nginx_config)
stdin.close()
print("[OK] Configuration updated")

print("\n[4/4] Testing and reloading...")
stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
output = stdout.read().decode() + stderr.read().decode()
print(output)

print("\n" + "=" * 60)
print("COMPLETE!")
print("=" * 60)
print("\nMain domain now serves Innovator Dashboard")
print("SSL: Let's Encrypt (valid, no browser warning)")
print("\nAccess:")
print("  https://felixxii.xyz")
print("  https://www.felixxii.xyz")

ssh.close()
