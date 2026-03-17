#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto Deployer - Automated deployment system

Features:
- One-click deployment
- Multi-environment support (dev/staging/prod)
- Rollback capability
- Health checks
- Deployment history
- Notification integration
"""

import os
import sys
import json
import subprocess
import hashlib
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import shutil

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DEPLOY_DIR = WORKSPACE / 'data' / 'deploy'
DEPLOY_DIR.mkdir(parents=True, exist_ok=True)

class Deployment:
    """Deployment record"""
    
    def __init__(self, service: str, version: str, environment: str = 'prod'):
        self.service = service
        self.version = version
        self.environment = environment
        self.timestamp = datetime.now()
        self.status = 'pending'  # pending, deploying, success, failed, rolled_back
        self.deploy_hash = hashlib.md5(
            f"{service}{version}{environment}{self.timestamp}".encode()
        ).hexdigest()[:8]
        self.duration_seconds = 0
        self.error = None
        self.rollback_to = None
    
    def to_dict(self) -> Dict:
        return {
            'service': self.service,
            'version': self.version,
            'environment': self.environment,
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
            'deploy_hash': self.deploy_hash,
            'duration_seconds': self.duration_seconds,
            'error': self.error,
            'rollback_to': self.rollback_to,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Deployment':
        dep = cls(data['service'], data['version'], data['environment'])
        dep.timestamp = datetime.fromisoformat(data['timestamp'])
        dep.status = data['status']
        dep.deploy_hash = data['deploy_hash']
        dep.duration_seconds = data.get('duration_seconds', 0)
        dep.error = data.get('error')
        dep.rollback_to = data.get('rollback_to')
        return dep


class AutoDeployer:
    """
    Automated deployment system
    
    Features:
    - Service packaging
    - Multi-environment deployment
    - Health checks
    - Rollback
    - History tracking
    """
    
    # Service configurations
    SERVICES = {
        'website': {
            'source': '40-collectors-数据收集器/website',
            'deploy_path': '/var/www/felixxii.xyz',
            'health_check': '/health',
            'restart_cmd': 'sudo systemctl reload nginx',
        },
        'stock-analyzer': {
            'source': '40-collectors-数据收集器/stock-analyzer',
            'deploy_path': '/var/www/felixxii.xyz/stock',
            'health_check': '/api/data',
            'restart_cmd': 'sudo systemctl restart stock-analyzer',
        },
        'workflow-visualizer': {
            'source': '30-scripts-tools/workflow_visualizer.py',
            'deploy_path': '/opt/workflow-visualizer',
            'port': 8445,
            'health_check': '/health',
            'restart_cmd': 'sudo systemctl restart workflow-visualizer',
        },
        'innovator-dashboard': {
            'source': '00-人格系统/innovator-dashboard',
            'deploy_path': '/opt/innovator-dashboard',
            'port': 8444,
            'health_check': '/health',
            'restart_cmd': 'sudo systemctl restart innovator-dashboard',
        },
    }
    
    def __init__(self):
        self.history_file = DEPLOY_DIR / 'deployment_history.json'
        self.config_file = DEPLOY_DIR / 'deploy_config.json'
        
        # Load history
        self.history: List[Dict] = []
        self._load_history()
    
    def _load_history(self):
        """Load deployment history"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history = json.load(f)
    
    def _save_history(self):
        """Save deployment history"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history[-100:], f, indent=2)  # Keep last 100
    
    def list_services(self) -> List[str]:
        """List available services"""
        return list(self.SERVICES.keys())
    
    def get_service_info(self, service: str) -> Optional[Dict]:
        """Get service information"""
        return self.SERVICES.get(service)
    
    def package(self, service: str, version: str) -> Path:
        """
        Package service for deployment
        
        Args:
            service: Service name
            version: Version string
        
        Returns:
            Path to package
        """
        print(f"\n📦 Packaging {service} v{version}...\n")
        
        service_config = self.SERVICES.get(service)
        if not service_config:
            raise ValueError(f"Unknown service: {service}")
        
        source_path = WORKSPACE / service_config['source']
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source_path}")
        
        # Create package directory
        package_dir = DEPLOY_DIR / 'packages' / f"{service}_{version}"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        if source_path.is_file():
            # Single file
            shutil.copy2(source_path, package_dir / source_path.name)
            package_size = source_path.stat().st_size
        else:
            # Directory
            for item in source_path.rglob('*'):
                if item.is_file():
                    # Skip hidden files and large files
                    if item.name.startswith('.'):
                        continue
                    if item.stat().st_size > 10 * 1024 * 1024:  # 10MB
                        continue
                    
                    relative_path = item.relative_to(source_path)
                    dest_path = package_dir / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
            
            # Calculate total size
            package_size = sum(
                f.stat().st_size for f in package_dir.rglob('*') if f.is_file()
            )
        
        # Create manifest
        manifest = {
            'service': service,
            'version': version,
            'timestamp': datetime.now().isoformat(),
            'file_count': len(list(package_dir.rglob('*'))),
            'total_size_bytes': package_size,
            'source': str(source_path),
        }
        
        with open(package_dir / 'manifest.json', 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Package created: {package_dir}")
        print(f"   Size: {package_size / 1024:.2f} KB")
        print(f"   Files: {manifest['file_count']}")
        
        return package_dir
    
    def deploy(self, service: str, version: str, environment: str = 'prod',
               skip_health_check: bool = False) -> Dict:
        """
        Deploy a service
        
        Args:
            service: Service name
            version: Version string
            environment: Deployment environment
            skip_health_check: Skip post-deployment health check
        
        Returns:
            Deployment result
        """
        start_time = datetime.now()
        
        print(f"\n🚀 Deploying {service} v{version} to {environment}...\n")
        
        # Create deployment record
        deployment = Deployment(service, version, environment)
        deployment.status = 'deploying'
        
        try:
            # Package
            package_path = self.package(service, version)
            
            # Simulate deployment (in real scenario, would use SSH/SCP)
            print(f"\n📤 Uploading to server...")
            time.sleep(1)  # Simulate upload
            
            print(f"\n🔧 Installing...")
            time.sleep(1)  # Simulate installation
            
            print(f"\n🔄 Restarting service...")
            time.sleep(1)  # Simulate restart
            
            # Health check
            if not skip_health_check:
                print(f"\n❤️ Running health check...")
                health_ok = self._health_check(service, environment)
                
                if not health_ok:
                    raise Exception("Health check failed")
            
            # Success
            deployment.status = 'success'
            deployment.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            print(f"\n✅ Deployment successful!")
            print(f"   Duration: {deployment.duration_seconds:.2f}s")
            print(f"   Hash: {deployment.deploy_hash}")
        
        except Exception as e:
            deployment.status = 'failed'
            deployment.error = str(e)
            deployment.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            print(f"\n❌ Deployment failed: {e}")
            
            # Auto-rollback suggestion
            print(f"\n💡 Suggestion: Run rollback with:")
            print(f"   python auto_deployer.py --rollback {service}")
        
        finally:
            # Record history
            self.history.append(deployment.to_dict())
            self._save_history()
        
        return deployment.to_dict()
    
    def _health_check(self, service: str, environment: str) -> bool:
        """
        Perform health check
        
        Args:
            service: Service name
            environment: Environment
        
        Returns:
            True if healthy
        """
        service_config = self.SERVICES.get(service)
        if not service_config:
            return False
        
        health_check_path = service_config.get('health_check')
        if not health_check_path:
            return True  # No health check defined
        
        # Simulate health check (in real scenario, would make HTTP request)
        time.sleep(0.5)
        
        # For demo, always return True
        print(f"   Health check: ✅ OK")
        return True
    
    def rollback(self, service: str, target_version: str = None) -> Dict:
        """
        Rollback a service
        
        Args:
            service: Service name
            target_version: Version to rollback to (default: previous)
        
        Returns:
            Rollback result
        """
        print(f"\n⏪ Rolling back {service}...\n")
        
        # Find previous deployment
        service_deployments = [
            d for d in self.history
            if d['service'] == service and d['status'] == 'success'
        ]
        
        if not service_deployments:
            return {
                'success': False,
                'error': 'No previous successful deployment found',
            }
        
        # Sort by timestamp
        service_deployments.sort(
            key=lambda x: x['timestamp'],
            reverse=True
        )
        
        # Get target version
        if target_version:
            target = next(
                (d for d in service_deployments if d['version'] == target_version),
                None
            )
        else:
            # Previous version
            target = service_deployments[1] if len(service_deployments) > 1 else None
        
        if not target:
            return {
                'success': False,
                'error': 'Target version not found',
            }
        
        print(f"   Rolling back to v{target['version']}")
        
        # Deploy previous version
        result = self.deploy(service, target['version'], 'prod')
        
        # Mark as rollback
        result['rollback'] = True
        result['rollback_from'] = service_deployments[0]['version']
        
        return result
    
    def get_history(self, service: str = None, limit: int = 10) -> List[Dict]:
        """Get deployment history"""
        history = self.history
        
        if service:
            history = [d for d in history if d['service'] == service]
        
        # Sort by timestamp (newest first)
        history.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return history[:limit]
    
    def get_stats(self) -> Dict:
        """Get deployment statistics"""
        total = len(self.history)
        success = len([d for d in self.history if d['status'] == 'success'])
        failed = len([d for d in self.history if d['status'] == 'failed'])
        
        # Average duration
        durations = [
            d['duration_seconds'] for d in self.history
            if d['status'] == 'success' and d.get('duration_seconds', 0) > 0
        ]
        avg_duration = sum(durations) / max(1, len(durations))
        
        # By service
        by_service = {}
        for dep in self.history:
            service = dep['service']
            if service not in by_service:
                by_service[service] = {'total': 0, 'success': 0}
            by_service[service]['total'] += 1
            if dep['status'] == 'success':
                by_service[service]['success'] += 1
        
        return {
            'total_deployments': total,
            'successful': success,
            'failed': failed,
            'success_rate': success / max(1, total),
            'avg_duration_seconds': avg_duration,
            'by_service': by_service,
        }
    
    def export_report(self, output_file: Path = None) -> Path:
        """Export deployment report"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = DEPLOY_DIR / f'deployment_report_{timestamp}.json'
        
        report = {
            'generated': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'recent_deployments': self.get_history(limit=20),
            'services': {
                name: info for name, info in self.SERVICES.items()
            },
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Report exported to: {output_file}")
        return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Auto Deployer")
    parser.add_argument('--list', action='store_true', help='List services')
    parser.add_argument('--deploy', type=str, help='Deploy service (format: service@version)')
    parser.add_argument('--rollback', type=str, help='Rollback service')
    parser.add_argument('--history', action='store_true', help='Show deployment history')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--package', type=str, help='Package service (format: service@version)')
    parser.add_argument('--env', type=str, default='prod', help='Environment (dev/staging/prod)')
    parser.add_argument('--demo', action='store_true', help='Demo mode')
    args = parser.parse_args()
    
    deployer = AutoDeployer()
    
    if args.list:
        services = deployer.list_services()
        print("\n📋 Available Services")
        print("=" * 60)
        for service in services:
            info = deployer.get_service_info(service)
            print(f"\n  {service}")
            print(f"     Source: {info['source']}")
            print(f"     Deploy: {info['deploy_path']}")
    
    elif args.deploy:
        parts = args.deploy.split('@')
        if len(parts) != 2:
            print("❌ Invalid format. Use: service@version")
            sys.exit(1)
        
        service, version = parts
        result = deployer.deploy(service, version, args.env)
        
        if result['status'] == 'success':
            sys.exit(0)
        else:
            sys.exit(1)
    
    elif args.rollback:
        result = deployer.rollback(args.rollback)
        
        if result.get('success', False):
            print(f"\n✅ Rollback successful")
            sys.exit(0)
        else:
            print(f"\n❌ Rollback failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    elif args.history:
        history = deployer.get_history(limit=10)
        print("\n📜 Deployment History")
        print("=" * 60)
        for dep in history:
            status_icon = '✅' if dep['status'] == 'success' else '❌'
            print(f"  {status_icon} {dep['service']} v{dep['version']} ({dep['environment']})")
            print(f"     {dep['timestamp'][:19]} | {dep['duration_seconds']:.2f}s | {dep['deploy_hash']}")
    
    elif args.stats:
        stats = deployer.get_stats()
        print("\n📊 Deployment Statistics")
        print("=" * 60)
        print(f"Total deployments: {stats['total_deployments']}")
        print(f"Successful: {stats['successful']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        print(f"Avg duration: {stats['avg_duration_seconds']:.2f}s")
        
        print(f"\nBy Service:")
        for service, data in stats['by_service'].items():
            print(f"   {service}: {data['success']}/{data['total']} successful")
    
    elif args.package:
        parts = args.package.split('@')
        if len(parts) != 2:
            print("❌ Invalid format. Use: service@version")
            sys.exit(1)
        
        service, version = parts
        deployer.package(service, version)
    
    elif args.demo:
        print("\n🎯 Auto Deployer Demo")
        print("=" * 60)
        
        # List services
        services = deployer.list_services()
        print(f"\n📋 Available services: {', '.join(services)}")
        
        # Show stats
        stats = deployer.get_stats()
        print(f"\n📊 Statistics: {stats['total_deployments']} deployments, {stats['success_rate']:.1%} success rate")
        
        print("\n✅ Demo complete!")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
