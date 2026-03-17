#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("FINDING CONFLICTING CONFIGS")
print("=" * 60)

print("\n[1/2] Searching for felixxii.xyz in all configs...")
stdin, stdout, stderr = ssh.exec_command("grep -r 'felixxii.xyz' /etc/nginx/ 2>/dev/null")
print(stdout.read().decode())

print("\n[2/2] Listing all conf.d files...")
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/conf.d/")
print(stdout.read().decode())

ssh.close()
