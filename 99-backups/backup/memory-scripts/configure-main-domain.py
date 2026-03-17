#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("CONFIGURING MAIN DOMAIN: felixxii.xyz")
print("=" * 60)

# Create SSL cert for main domain
print("\n[1/5] Generating SSL certificate for felixxii.xyz...")
stdin, stdout, stderr = ssh.exec_command("""
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/felixxii.key \
  -out /etc/nginx/ssl/felixxii.crt \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Felixxii/CN=felixxii.xyz"
""")
print(stdout.read().decode() + stderr.read().decode())

# Create nginx config for main domain
nginx_config = """# Main domain - HTTPS
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name felixxii.xyz www.felixxii.xyz;
    
    # SSL certificates
    ssl_certificate     /etc/nginx/ssl/felixxii.crt;
    ssl_certificate_key /etc/nginx/ssl/felixxii.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Redirect to innovator dashboard
    location / {
        return 301 https://$host:8444$request_uri;
    }
    
    # Or serve innovator content directly
    # root /var/www/innovator;
    # index index.html;
    # location / {
    #     try_files $uri $uri/ =404;
    # }
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

print("\n[2/5] Writing nginx configuration...")
stdin, stdout, stderr = ssh.exec_command("tee /etc/nginx/conf.d/felixxii-main.conf > /dev/null")
stdin.write(nginx_config)
stdin.close()
print("[OK] Configuration written")

print("\n[3/5] Testing nginx configuration...")
stdin, stdout, stderr = ssh.exec_command("nginx -t")
output = stdout.read().decode() + stderr.read().decode()
print(output)

print("\n[4/5] Reloading nginx...")
stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
print(stdout.read().decode() + stderr.read().decode())

print("\n[5/5] Verifying configuration...")
stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep -E ':80|:443|:8444'")
print(stdout.read().decode())

print("\n" + "=" * 60)
print("MAIN DOMAIN CONFIGURATION COMPLETE!")
print("=" * 60)
print("\nAccess URLs:")
print("  https://felixxii.xyz (redirects to :8444)")
print("  https://www.felixxii.xyz (redirects to :8444)")
print("  https://felixxii.xyz:8444 (direct)")
print("\nNote: Self-signed SSL - browser will show warning")

ssh.close()
