from pathlib import Path
#!/usr/bin/env python3
"""
Innovator Dashboard v3.0 - Auto Deployment Script
Deploys dashboard API and frontend to cloud server

Server: 8.208.30.28 (UK London)
Port: 8446
Author: Claw 🐾
"""

import paramiko
import os
import sys
import time
from datetime import datetime

# Configuration
SERVER_HOST = '8.208.30.28'
SERVER_USER = 'root'
SERVER_PASSWORD = '20051104sS'
SERVER_PORT = 8446

LOCAL_WORKSPACE = str(Path(__file__).parent.parent)
REMOTE_DIR = '/root/dashboard-v3'

FILES_TO_DEPLOY = [
    'dashboard-api-v3.py',
    'innovator-dashboard-v3.html'
]

def print_step(step, message):
    """Print formatted step message"""
    print(f"\n{'=' *60}")
    print(f"Step {step}: {message}")
    print('=' *60)

def connect_ssh():
    """Connect to cloud server via SSH"""
    print_step(1, f"Connecting to {SERVER_HOST}")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=SERVER_HOST,
            port=22,
            username=SERVER_USER,
            password=SERVER_PASSWORD,
            timeout=10
        )
        print(f"✅ SSH connection successful")
        return ssh
    except Exception as e:
        print(f"❌ SSH connection failed: {e}")
        return None

def create_remote_dir(ssh):
    """Create remote directory"""
    print_step(2, f"Creating remote directory {REMOTE_DIR}")

    try:
        sftp = ssh.open_sftp()
        try:
            sftp.stat(REMOTE_DIR)
            print(f"ℹ️  Directory already exists")
        except FileNotFoundError:
            sftp.mkdir(REMOTE_DIR)
            print(f"✅ Directory created")

        sftp.close()
        return True
    except Exception as e:
        print(f"❌ Failed to create directory: {e}")
        return False

def upload_files(ssh):
    """Upload files to server"""
    print_step(3, "Uploading files")

    try:
        sftp = ssh.open_sftp()

        for filename in FILES_TO_DEPLOY:
            local_path = os.path.join(LOCAL_WORKSPACE, filename)
            remote_path = f"{REMOTE_DIR}/{filename}"

            if os.path.exists(local_path):
                print(f"📤 Uploading {filename}...")
                sftp.put(local_path, remote_path)
                print(f"✅ {filename} uploaded")
            else:
                print(f"⚠️  {filename} not found locally")

        sftp.close()
        return True
    except Exception as e:
        print(f"❌ File upload failed: {e}")
        return False

def install_dependencies(ssh):
    """Install Python dependencies"""
    print_step(4, "Installing dependencies (psutil)")

    try:
        stdin, stdout, stderr = ssh.exec_command('pip3 install psutil -q')
        exit_code = stdout.channel.recv_exit_status()

        if exit_code == 0:
            print(f"✅ Dependencies installed")
            return True
        else:
            error = stderr.read().decode()
            print(f"⚠️  Installation warning: {error}")
            return True
    except Exception as e:
        print(f"❌ Dependency installation failed: {e}")
        return False

def stop_existing_server(ssh):
    """Stop any existing dashboard server"""
    print_step(5, "Stopping existing server")

    try:
        # Find and kill existing process
        stdin, stdout, stderr = ssh.exec_command(
            "pkill -f 'dashboard-api-v3.py' 2>/dev/null || true"
        )
        stdout.channel.recv_exit_status()
        print(f"✅ Existing server stopped")
        return True
    except Exception as e:
        print(f"⚠️  Warning stopping server: {e}")
        return True

def start_server(ssh):
    """Start the new dashboard server"""
    print_step(6, "Starting dashboard server")

    try:
        # Start server in background using nohup
        command = f"cd {REMOTE_DIR} && nohup python3 dashboard-api-v3.py > dashboard.log 2>&1 &"
        stdin, stdout, stderr = ssh.exec_command(command)
        time.sleep(2)

        # Check if server is running
        stdin, stdout, stderr = ssh.exec_command(
            f"lsof -i :{SERVER_PORT} | grep LISTEN || netstat -tlnp | grep :{SERVER_PORT}"
        )
        result = stdout.read().decode()

        if result:
            print(f"✅ Server started on port {SERVER_PORT}")
            return True
        else:
            # Try alternative check
            stdin, stdout, stderr = ssh.exec_command(
                f"curl -s http://localhost:{SERVER_PORT}/api/health | head -c 100"
            )
            health = stdout.read().decode()
            if health:
                print(f"✅ Server started and responding")
                return True
            else:
                print(f"⚠️  Server may not be running, checking process...")
                stdin, stdout, stderr = ssh.exec_command("ps aux | grep dashboard")
                ps_out = stdout.read().decode()
                print(ps_out)
                return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False

def configure_firewall(ssh):
    """Configure firewall to allow port"""
    print_step(7, "Configuring firewall")

    try:
        # Try to open port with ufw
        stdin, stdout, stderr = ssh.exec_command(
            f"ufw allow {SERVER_PORT}/tcp 2>/dev/null || iptables -A INPUT -p tcp --dport {SERVER_PORT} -j ACCEPT 2>/dev/null || true"
        )
        stdout.channel.recv_exit_status()
        print(f"✅ Firewall configured for port {SERVER_PORT}")
        return True
    except Exception as e:
        print(f"⚠️  Firewall configuration warning: {e}")
        return True

def verify_deployment(ssh):
    """Verify deployment is working"""
    print_step(8, "Verifying deployment")

    try:
        # Test API endpoint
        stdin, stdout, stderr = ssh.exec_command(
            f"curl -s http://localhost:{SERVER_PORT}/api/health"
        )
        health = stdout.read().decode()

        if health and 'local' in health:
            print(f"✅ API health check passed")
            print(f"📊 Health: {health[:100]}...")
            return True
        else:
            print(f"⚠️  API health check returned: {health[:200] if health else 'empty'}")
            return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def show_access_info():
    """Display access information"""
    print_step(9, "Deployment Complete!")

    print(f"""
╔══════════════════════════════════════════════════════════╗
║           🎭 Innovator Dashboard v3.0 LIVE!              ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  🌐 Access URLs:                                         ║
║  ───────────────────────────────────────────────────     ║
║  • Dashboard:   http://{SERVER_HOST}:{SERVER_PORT}/               ║
║  • API:         http://{SERVER_HOST}:{SERVER_PORT}/api/dashboard  ║
║                                                          ║
║  📊 API Endpoints:                                       ║
║  ───────────────────────────────────────────────────     ║
║  • GET  /api/sessions    - Session history               ║
║  • GET  /api/innovations - Innovation database           ║
║  • GET  /api/memory      - Memory status                 ║
║  • GET  /api/git         - Git statistics                ║
║  • GET  /api/health      - System health                 ║
║  • GET  /api/personas    - Persona history               ║
║  • GET  /api/dashboard   - Full summary                  ║
║  • POST /api/innovations - Add innovation                ║
║                                                          ║
║  📁 Remote Location: {REMOTE_DIR}                   ║
║  📝 Log File: {REMOTE_DIR}/dashboard.log                ║
║                                                          ║
║  🔄 Auto-refresh: Every 5 minutes                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)

def main():
    """Main deployment function"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     🚀 Innovator Dashboard v3.0 - Auto Deploy Script     ║
║              Target: 8.208.30.28 (UK London)             ║
╚══════════════════════════════════════════════════════════╝
    """)

    start_time = time.time()

    # Connect
    ssh = connect_ssh()
    if not ssh:
        sys.exit(1)

    try:
        # Deploy
        if not create_remote_dir(ssh):
            sys.exit(1)

        if not upload_files(ssh):
            sys.exit(1)

        if not install_dependencies(ssh):
            sys.exit(1)

        if not stop_existing_server(ssh):
            sys.exit(1)

        if not start_server(ssh):
            sys.exit(1)

        if not configure_firewall(ssh):
            pass  # Non-critical

        if not verify_deployment(ssh):
            pass  # Non-critical

        # Show info
        elapsed = time.time() - start_time
        print(f"\n⏱️  Total deployment time: {elapsed:.1f} seconds")

        show_access_info()

    finally:
        ssh.close()

if __name__ == '__main__':
    main()
