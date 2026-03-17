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
print("CONFIGURING NGINX FOR INNOVATOR DASHBOARD")
print("=" * 60)

# Create nginx config for conf.d
nginx_config = """server {
    listen 8443 ssl http2;
    server_name innovator.felixxii.xyz;
    
    # SSL certificates (will be configured later)
    # ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    
    # Temporary self-signed for testing
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

print("\n[1/4] Creating SSL directory...")
stdin, stdout, stderr = ssh.exec_command("mkdir -p /etc/nginx/ssl")
print(stdout.read().decode() + stderr.read().decode())

print("\n[2/4] Generating self-signed SSL certificate...")
stdin, stdout, stderr = ssh.exec_command("""
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/innovator.key \
  -out /etc/nginx/ssl/innovator.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Innovator/CN=innovator.felixxii.xyz"
""")
ssl_output = stdout.read().decode() + stderr.read().decode()
print(ssl_output if ssl_output else "[OK] Certificate generated")

print("\n[3/4] Writing nginx configuration...")
# Use tee to write file
stdin, stdout, stderr = ssh.exec_command(f"tee /etc/nginx/conf.d/innovator.conf > /dev/null")
stdin.write(nginx_config)
stdin.close()
print("[OK] Configuration written to /etc/nginx/conf.d/innovator.conf")

print("\n[4/4] Testing and reloading nginx...")
stdin, stdout, stderr = ssh.exec_command("nginx -t && systemctl reload nginx")
output = stdout.read().decode() + stderr.read().decode()
print(output)

# Verify
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/conf.d/innovator.conf")
print(f"Config file: {stdout.read().decode().strip()}")

stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/ssl/")
print(f"\nSSL files:\n{stdout.read().decode()}")

stdin, stdout, stderr = ssh.exec_command("systemctl status nginx --no-pager | head -5")
print(f"\nnginx status:\n{stdout.read().decode()}")

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE!")
print("=" * 60)
print(f"\nAccess URL: https://8.208.30.28:8443")
print(f"Domain URL: https://innovator.felixxii.xyz:8443")
print("\nNote: Using self-signed SSL certificate.")
print("To install Let's Encrypt cert later, run certbot.")

ssh.close()
