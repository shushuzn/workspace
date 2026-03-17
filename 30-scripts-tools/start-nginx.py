#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("[1/2] Starting nginx...")
stdin, stdout, stderr = ssh.exec_command("systemctl start nginx && systemctl status nginx --no-pager | head -10")
print(stdout.read().decode())

print("\n[2/2] Testing access...")
stdin, stdout, stderr = ssh.exec_command("curl -k -I https://localhost:8444 2>&1")
print(stdout.read().decode())

print("\n[3/3] Checking ports...")
stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep -E '80|443|8443|8444'")
print(stdout.read().decode())

ssh.close()
