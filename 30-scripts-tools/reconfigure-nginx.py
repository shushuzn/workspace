#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"
REMOTE_PATH = "/var/www/innovator"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("RECONFIGURING INNOVATOR DASHBOARD (PORT 8444)")
print("=" * 60)

# Updated nginx config for port 8444
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

print("\n[1/3] Updating nginx configuration (port 8444)...")
stdin, stdout, stderr = ssh.exec_command("tee /etc/nginx/conf.d/innovator.conf > /dev/null")
stdin.write(nginx_config)
stdin.close()
print("[OK] Configuration updated")

print("\n[2/3] Testing nginx...")
stdin, stdout, stderr = ssh.exec_command("nginx -t")
output = stdout.read().decode() + stderr.read().decode()
print(output)

print("\n[3/3] Reloading nginx...")
stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
print(stdout.read().decode() + stderr.read().decode())

# Verify
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("curl -k -I https://localhost:8444 2>&1 | head -5")
print(stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep -E '8443|8444'")
print("\nPort status:")
print(stdout.read().decode())

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE!")
print("=" * 60)
print(f"\nAccess URL: https://8.208.30.28:8444")
print(f"Domain URL: https://innovator.felixxii.xyz:8444")
print("\nNote: Port 8443 = code-server (CoPaw IDE)")
print("      Port 8444 = Innovator Dashboard")

ssh.close()
