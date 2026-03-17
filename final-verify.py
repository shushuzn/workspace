#!/usr/bin/env python3
import paramiko

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)

print("=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

print("\n[1/3] Checking nginx config files...")
stdin, stdout, stderr = ssh.exec_command("ls -la /etc/nginx/conf.d/")
print(stdout.read().decode())

print("\n[2/3] Checking active server blocks...")
stdin, stdout, stderr = ssh.exec_command("nginx -T 2>&1 | grep -E 'server_name|listen.*443'")
result = stdout.read().decode()
print(result[:2000] if len(result) > 2000 else result)

print("\n[3/3] Testing all access methods...")
print("\n  Main domain (443):")
stdin, stdout, stderr = ssh.exec_command("curl -k -s -o /dev/null -w '%{http_code}' https://localhost:443")
print(f"    HTTP {stdout.read().decode()}")

print("\n  Innovator port (8444):")
stdin, stdout, stderr = ssh.exec_command("curl -k -s -o /dev/null -w '%{http_code}' https://localhost:8444")
print(f"    HTTP {stdout.read().decode()}")

print("\n  Content check:")
stdin, stdout, stderr = ssh.exec_command("curl -k -s https://localhost:443 | grep -o '<title>.*</title>'")
print(f"    {stdout.read().decode()}")

ssh.close()
