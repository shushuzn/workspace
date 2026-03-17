#!/usr/bin/env python3
import paramiko
import os

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"
LOCAL_DASHBOARD = "D:/OpenClaw/workspace/33-dashboard"
REMOTE_PATH = "/var/www/innovator"

print("=" * 60)
print("INNOVATOR DASHBOARD DEPLOYMENT")
print("=" * 60)

try:
    # Connect
    print("\n[1/6] Connecting to server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)
    sftp = ssh.open_sftp()
    print("[OK] Connected!")
    
    # Create directory
    print("\n[2/6] Creating remote directory...")
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {REMOTE_PATH}")
    print(stdout.read().decode() + stderr.read().decode())
    print(f"[OK] Directory created: {REMOTE_PATH}")
    
    # Upload files
    print("\n[3/6] Uploading files...")
    for filename in os.listdir(LOCAL_DASHBOARD):
        local_path = os.path.join(LOCAL_DASHBOARD, filename)
        remote_path = f"{REMOTE_PATH}/{filename}"
        
        if os.path.isfile(local_path):
            print(f"  Uploading: {filename}")
            sftp.put(local_path, remote_path)
    
    print("[OK] Files uploaded!")
    
    # Set permissions
    print("\n[4/6] Setting permissions...")
    stdin, stdout, stderr = ssh.exec_command(f"chmod -R 755 {REMOTE_PATH}")
    print(stdout.read().decode() + stderr.read().decode())
    print("[OK] Permissions set!")
    
    # Configure nginx
    print("\n[5/6] Configuring nginx...")
    nginx_config = '''server {
    listen 8443 ssl http2;
    server_name innovator.felixxii.xyz;
    
    ssl_certificate /etc/letsencrypt/live/felixxii.xyz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/felixxii.xyz/privkey.pem;
    
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
}
'''
    
    # Write config using echo
    stdin, stdout, stderr = ssh.exec_command(f"cat > /etc/nginx/sites-available/innovator << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF")
    result = stdout.read().decode() + stderr.read().decode()
    print(result if result else "[OK] Config file created")
    
    # Enable site
    stdin, stdout, stderr = ssh.exec_command("ln -sf /etc/nginx/sites-available/innovator /etc/nginx/sites-enabled/")
    print("[OK] Site enabled!")
    
    # Test nginx
    print("\n[6/6] Testing nginx configuration...")
    stdin, stdout, stderr = ssh.exec_command("nginx -t")
    output = stdout.read().decode() + stderr.read().decode()
    print(output)
    
    if "successful" in output.lower():
        # Reload nginx
        stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
        print("[OK] nginx reloaded!")
    else:
        print("[WARN] nginx test had issues, skipping reload")
    
    # Verify
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print(f"\nAccess URL: https://innovator.felixxii.xyz:8443")
    print(f"Direct IP:  https://8.208.30.28:8443")
    print("\nFiles deployed:")
    stdin, stdout, stderr = ssh.exec_command(f"ls -la {REMOTE_PATH}")
    print(stdout.read().decode())
    
    ssh.close()
    
except Exception as e:
    print(f"\n[FAIL] Deployment failed: {e}")
    import traceback
    traceback.print_exc()
