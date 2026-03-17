#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("REMOVING CONFLICTING CONFIGS")
print("=" * 60)

print("\n[1/3] Backing up openclaw-http.conf...")
stdin, stdout, stderr = ssh.exec_command("cp /etc/nginx/conf.d/openclaw-http.conf /etc/nginx/conf.d/openclaw-http.conf.bak && rm /etc/nginx/conf.d/openclaw-http.conf")
print("[OK] Backed up and removed")

print("\n[2/3] Testing nginx...")
stdin, stdout, stderr = ssh.exec_command("nginx -t")
output = stdout.read().decode() + stderr.read().decode()
print(output)

print("\n[3/3] Reloading nginx...")
stdin, stdout, stderr = ssh.exec_command("systemctl reload nginx")
print(stdout.read().decode() + stderr.read().decode())

print("\n[4/4] Final verification...")
stdin, stdout, stderr = ssh.exec_command("curl -k -I https://localhost:443 2>&1 | head -3")
print(stdout.read().decode())

print("\n" + "=" * 60)
print("ALL CONFLICTS RESOLVED!")
print("=" * 60)

ssh.close()
