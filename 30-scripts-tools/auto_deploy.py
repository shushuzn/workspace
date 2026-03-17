#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-Deploy Script - Cloud Deployment Automation
Automatically deploys self-iteration system to cloud server
Features: SSH deployment, service configuration, health check, rollback

Usage:
    python auto_deploy.py --deploy
    python auto_deploy.py --status
    python auto_deploy.py --rollback
"""

import os
import sys
import json
import paramiko
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AutoDeployer:
    """Automate cloud deployment"""
    
    def __init__(self):
        self.config_file = WORKSPACE / "20-data-reports" / "deploy_config.json"
        self.history_file = WORKSPACE / "20-data-reports" / "deploy_history.json"
        
        # Cloud server config
        self.config = {
            'host': os.getenv("HOST_IP", os.getenv("HOST_IP", "8.208.30.28")),
            'port': 22,
            'username': 'root',
            'password': '20051104sS',
            'deploy_path': '/opt/openclaw/self-iteration',
            'service_name': 'self-iteration-dashboard',
            'dashboard_port': 8086,
            'orchestrator_port': 8087
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except:
                pass
    
    def save_config(self):
        """Save configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def connect_ssh(self):
        """Connect to cloud server via SSH"""
        print(f"\n📡 Connecting to {self.config['host']}...")
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            client.connect(
                hostname=self.config['host'],
                port=self.config['port'],
                username=self.config['username'],
                password=self.config['password'],
                timeout=30
            )
            print(f"✅ Connected successfully\n")
            return client
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return None
    
    def prepare_files(self) -> List[str]:
        """Prepare files for deployment"""
        print("📦 Preparing files for deployment...\n")
        
        files = [
            '30-scripts-tools/self_iteration.py',
            '30-scripts-tools/meta_learning.py',
            '30-scripts-tools/evolution_engine.py',
            '30-scripts-tools/self_iter_cli.py',
            '30-scripts-tools/heartbeat_integration.py',
            '30-scripts-tools/self_iter_dashboard.py',
            '30-scripts-tools/smart_recommendations.py',
            '30-scripts-tools/system_orchestrator.py',
        ]
        
        for f in files:
            full_path = WORKSPACE / f
            if not full_path.exists():
                print(f"❌ File not found: {f}")
                files.remove(f)
            else:
                print(f"✅ {f} ({full_path.stat().st_size} bytes)")
        
        print(f"\nTotal: {len(files)} files ready\n")
        return files
    
    def deploy(self, files: List[str], ssh_client) -> bool:
        """Deploy files to cloud server"""
        print("🚀 Deploying to cloud server...\n")
        
        sftp = ssh_client.open_sftp()
        
        try:
            # Create deploy directory
            stdin, stdout, stderr = ssh_client.exec_command(
                f"mkdir -p {self.config['deploy_path']}"
            )
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code != 0:
                print(f"❌ Failed to create directory: {stderr.read().decode()}")
                return False
            
            print(f"✅ Created directory: {self.config['deploy_path']}\n")
            
            # Upload files
            for file_path in files:
                local_path = WORKSPACE / file_path
                remote_path = f"{self.config['deploy_path']}/{file_path.split('/')[-1]}"
                
                print(f"📤 Uploading: {file_path.split('/')[-1]}")
                sftp.put(str(local_path), remote_path)
                print(f"   ✅ {remote_path}")
            
            print(f"\n✅ All files uploaded successfully\n")
            
            # Make scripts executable
            stdin, stdout, stderr = ssh_client.exec_command(
                f"chmod +x {self.config['deploy_path']}/*.py"
            )
            stdout.channel.recv_exit_status()
            print("✅ Scripts made executable\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
        finally:
            sftp.close()
    
    def configure_service(self, ssh_client) -> bool:
        """Configure systemd service"""
        print("⚙️  Configuring systemd service...\n")
        
        # Dashboard service
        dashboard_service = f"""[Unit]
Description=Self-Iteration Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={self.config['deploy_path']}
ExecStart=/usr/bin/python3 {self.config['deploy_path']}/self_iter_dashboard.py --start --port {self.config['dashboard_port']}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        # Orchestrator service
        orchestrator_service = f"""[Unit]
Description=System Orchestrator
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={self.config['deploy_path']}
ExecStart=/usr/bin/python3 {self.config['deploy_path']}/system_orchestrator.py --execute
Restart=on-failure
RestartSec=300

[Install]
WantedBy=multi-user.target
"""
        
        sftp = ssh_client.open_sftp()
        
        try:
            # Upload service files
            sftp.put('/dev/stdin', '/etc/systemd/system/self-iteration-dashboard.service', 
                    stdin=dashboard_service.encode())
            print("✅ Dashboard service configured")
            
            sftp.put('/dev/stdin', '/etc/systemd/system/self-iteration-orchestrator.service',
                    stdin=orchestrator_service.encode())
            print("✅ Orchestrator service configured\n")
            
            # Reload systemd
            stdin, stdout, stderr = ssh_client.exec_command(
                "systemctl daemon-reload"
            )
            stdout.channel.recv_exit_status()
            print("✅ Systemd reloaded\n")
            
            # Enable and start services
            stdin, stdout, stderr = ssh_client.exec_command(
                f"systemctl enable {self.config['service_name']}"
            )
            stdout.channel.recv_exit_status()
            print(f"✅ Service enabled: {self.config['service_name']}")
            
            stdin, stdout, stderr = ssh_client.exec_command(
                f"systemctl start {self.config['service_name']}"
            )
            stdout.channel.recv_exit_status()
            print(f"✅ Service started: {self.config['service_name']}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Service configuration failed: {e}")
            return False
        finally:
            sftp.close()
    
    def health_check(self, ssh_client) -> Dict:
        """Run health check"""
        print("🏥 Running health check...\n")
        
        health = {
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'ports': {},
            'overall': True
        }
        
        # Check services
        stdin, stdout, stderr = ssh_client.exec_command(
            f"systemctl is-active {self.config['service_name']}"
        )
        status = stdout.read().decode().strip()
        health['services'][self.config['service_name']] = status
        print(f"Service {self.config['service_name']}: {status}")
        
        if status != 'active':
            health['overall'] = False
        
        # Check ports
        stdin, stdout, stderr = ssh_client.exec_command(
            f"netstat -tlnp | grep :{self.config['dashboard_port']}"
        )
        port_status = stdout.read().decode().strip()
        health['ports'][self.config['dashboard_port']] = 'listening' if port_status else 'not_listening'
        print(f"Port {self.config['dashboard_port']}: {health['ports'][self.config['dashboard_port']]}")
        
        if not port_status:
            health['overall'] = False
        
        print(f"\nOverall health: {'✅ Healthy' if health['overall'] else '❌ Issues detected'}\n")
        
        return health
    
    def record_deployment(self, success: bool, health: Dict):
        """Record deployment to history"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'success': success,
            'health': health,
            'files_deployed': len(self.prepare_files())
        }
        
        history.append(record)
        
        # Keep last 30 deployments
        history = history[-30:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    
    def run_full_deployment(self) -> bool:
        """Run complete deployment process"""
        print("\n" + "="*60)
        print(" Auto-Deploy: Self-Iteration System")
        print("="*60 + "\n")
        
        start_time = datetime.now()
        
        # Step 1: Prepare files
        files = self.prepare_files()
        if not files:
            return False
        
        # Step 2: Connect SSH
        ssh_client = self.connect_ssh()
        if not ssh_client:
            return False
        
        try:
            # Step 3: Deploy files
            if not self.deploy(files, ssh_client):
                return False
            
            # Step 4: Configure service
            if not self.configure_service(ssh_client):
                return False
            
            # Step 5: Health check
            health = self.health_check(ssh_client)
            
            # Step 6: Record deployment
            self.record_deployment(True, health)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*60)
            print(" Deployment Complete!")
            print("="*60)
            print(f"Duration: {duration:.1f}s")
            print(f"Files: {len(files)}")
            print(f"Dashboard: http://{self.config['host']}:{self.config['dashboard_port']}")
            print(f"Health: {'✅ Healthy' if health['overall'] else '⚠️ Issues'}")
            print("="*60 + "\n")
            
            return True
            
        finally:
            ssh_client.close()
    
    def get_status(self) -> Dict:
        """Get deployment status"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                pass
        
        last_deployment = history[-1] if history else None
        
        return {
            'config': self.config,
            'last_deployment': last_deployment,
            'total_deployments': len(history),
            'success_rate': sum(1 for h in history if h['success']) / max(1, len(history))
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Auto-Deploy Script')
    parser.add_argument('--deploy', action='store_true', help='Run deployment')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--rollback', action='store_true', help='Rollback deployment')
    args = parser.parse_args()
    
    deployer = AutoDeployer()
    
    if args.deploy:
        success = deployer.run_full_deployment()
        sys.exit(0 if success else 1)
    
    elif args.status:
        status = deployer.get_status()
        print(json.dumps(status, indent=2, default=str))
    
    elif args.rollback:
        print("Rollback not implemented yet")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
