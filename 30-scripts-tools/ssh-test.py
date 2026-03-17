#!/usr/bin/env python3
import paramiko
import sys

HOST = "8.208.30.28"
USER = "root"
PASSWORD = "20051104sS"

print("[TEST] Testing SSH connection...")
print(f"Target: {USER}@{HOST}")

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=PASSWORD, timeout=10)
    
    print("[OK] Connection successful!")
    
    # Test commands
    commands = [
        "whoami",
        "hostname", 
        "pwd",
        "ls -la /var/www/ 2>/dev/null || echo 'Directory check'",
        "nginx -v 2>&1 || echo 'nginx not found'"
    ]
    
    for cmd in commands:
        print(f"\n[CMD] Running: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if output:
            print(output.strip())
        if error:
            print(error.strip())
    
    ssh.close()
    print("\n[OK] SSH test complete!")
    
except Exception as e:
    print(f"[FAIL] Connection failed: {e}")
    sys.exit(1)
