#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"
LOCAL_FILE = "D:/OpenClaw/workspace/innovator-dashboard.html"
REMOTE_PATH = "/var/www/innovator/index.html"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("DEPLOYING INNOVATOR DASHBOARD")
print("=" * 60)

print("\n[1/3] Uploading innovator-dashboard.html...")
sftp = ssh.open_sftp()
sftp.put(LOCAL_FILE, REMOTE_PATH)
print(f"[OK] Uploaded to {REMOTE_PATH}")

print("\n[2/3] Setting permissions...")
stdin, stdout, stderr = ssh.exec_command(f"chmod 644 {REMOTE_PATH}")
print(stdout.read().decode() + stderr.read().decode())

print("\n[3/3] Verifying deployment...")
stdin, stdout, stderr = ssh.exec_command(f"ls -lh {REMOTE_PATH}")
print(stdout.read().decode())

stdin, stdout, stderr = ssh.exec_command(f"grep -o '<title>.*</title>' {REMOTE_PATH}")
print(f"Title: {stdout.read().decode()}")

print("\n" + "=" * 60)
print("DEPLOYMENT COMPLETE!")
print("=" * 60)
print("\nAccess URLs:")
print("  https://felixxii.xyz")
print("  https://www.felixxii.xyz")
print("  https://8.208.30.28:8444")

ssh.close()
