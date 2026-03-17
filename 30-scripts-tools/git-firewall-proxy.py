#!/usr/bin/env python3
"""
Git Firewall Proxy Server
=========================
Real-time Git operation scanner and blocker for sensitive data prevention.

Features:
- Pattern matching for .env, tokens, secrets
- Entropy analysis for encrypted/binary sensitive data
- File size limits
- Path blacklist
- Token format validation
- Real-time blocking with detailed reports

Usage:
    python git-firewall-proxy.py --port 8080 --mode proxy
    python git-firewall-proxy.py --scan /path/to/repo
"""

import os
import re
import sys
import math
import json
import hashlib
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Configuration
# ============================================================================

class FirewallConfig:
    """Firewall configuration and rules"""
    
    # Sensitive file patterns
    SENSITIVE_FILES = [
        r'.*\.env$',
        r'.*\.env\..*$',
        r'.*\.pem$',
        r'.*\.key$',
        r'.*\.p12$',
        r'.*\.pfx$',
        r'.*credentials.*',
        r'.*secrets.*',
        r'.*password.*',
    ]
    
    # Secret patterns (regex)
    SECRET_PATTERNS = [
        (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
        (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', 'GitHub Fine-grained Token'),
        (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth Token'),
        (r'ghu_[a-zA-Z0-9]{36}', 'GitHub User-to-Server Token'),
        (r'ghs_[a-zA-Z0-9]{36}', 'GitHub Server-to-Server Token'),
        (r'sk-[a-zA-Z0-9]{48}', 'OpenAI API Key'),
        (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
        (r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----', 'Private Key'),
        (r'api[_-]?key[\'"]?\s*[:=]\s*[\'"][a-zA-Z0-9]{20,}[\'"]', 'API Key'),
        (r'password[\'"]?\s*[:=]\s*[\'"][^\'"]{8,}[\'"]', 'Hardcoded Password'),
        (r'secret[\'"]?\s*[:=]\s*[\'"][^\'"]{16,}[\'"]', 'Secret Key'),
    ]
    
    # Path blacklist
    BLACKLISTED_PATHS = [
        'credentials/',
        'secrets/',
        'private/',
        '.ssh/',
        'keys/',
        'certificates/',
    ]
    
    # File size limit (bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Entropy threshold (high entropy = likely encrypted/random = potential secret)
    ENTROPY_THRESHOLD = 7.5
    
    # Minimum secret length
    MIN_SECRET_LENGTH = 20


# ============================================================================
# Detection Engine
# ============================================================================

class DetectionEngine:
    """Core detection engine for sensitive data"""
    
    def __init__(self, config: FirewallConfig = None):
        self.config = config or FirewallConfig()
        self.stats = {
            'scanned': 0,
            'blocked': 0,
            'warnings': 0,
            'passed': 0,
        }
    
    def calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data"""
        if not data:
            return 0.0
        
        entropy = 0.0
        byte_counts = {}
        
        for byte in data:
            byte_counts[byte] = byte_counts.get(byte, 0) + 1
        
        data_len = len(data)
        for count in byte_counts.values():
            if count > 0:
                probability = count / data_len
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def check_file_path(self, file_path: str) -> Tuple[bool, List[str]]:
        """Check if file path matches sensitive patterns"""
        issues = []
        
        # Check sensitive file patterns
        for pattern in self.config.SENSITIVE_FILES:
            if re.match(pattern, file_path, re.IGNORECASE):
                issues.append(f"Sensitive file pattern matched: {pattern}")
        
        # Check blacklisted paths
        for blacklisted in self.config.BLACKLISTED_PATHS:
            if blacklisted.lower() in file_path.lower():
                issues.append(f"Blacklisted path detected: {blacklisted}")
        
        return len(issues) == 0, issues
    
    def check_file_content(self, content: bytes, file_path: str = "") -> Tuple[bool, List[str]]:
        """Check file content for secrets"""
        issues = []
        
        # Try to decode as text
        try:
            text_content = content.decode('utf-8', errors='ignore')
        except:
            text_content = ""
        
        # Check secret patterns
        for pattern, secret_type in self.config.SECRET_PATTERNS:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                issues.append(f"{secret_type} detected ({len(matches)} matches)")
        
        # Check entropy for text files
        if file_path.endswith(('.txt', '.md', '.py', '.js', '.json', '.yaml', '.yml')):
            entropy = self.calculate_entropy(content)
            if entropy > self.config.ENTROPY_THRESHOLD:
                issues.append(f"High entropy detected: {entropy:.2f} (threshold: {self.config.ENTROPY_THRESHOLD})")
        
        # Check for long random strings
        long_strings = re.findall(r'[a-zA-Z0-9+/=]{32,}', text_content)
        for s in long_strings:
            if len(s) >= self.config.MIN_SECRET_LENGTH:
                entropy = self.calculate_entropy(s.encode())
                if entropy > 6.0:
                    issues.append(f"Potential secret string detected (entropy: {entropy:.2f})")
        
        return len(issues) == 0, issues
    
    def check_file_size(self, size: int) -> Tuple[bool, List[str]]:
        """Check file size limit"""
        if size > self.config.MAX_FILE_SIZE:
            return False, [f"File size exceeds limit: {size / 1024 / 1024:.2f}MB (max: {self.config.MAX_FILE_SIZE / 1024 / 1024}MB)"]
        return True, []
    
    def scan_file(self, file_path: str, content: bytes = None) -> Dict:
        """Scan a single file"""
        self.stats['scanned'] += 1
        
        result = {
            'file': file_path,
            'status': 'PASS',
            'issues': [],
            'severity': 'NONE',
        }
        
        # Check file path
        path_ok, path_issues = self.check_file_path(file_path)
        if not path_ok:
            result['issues'].extend(path_issues)
            result['status'] = 'BLOCK'
            result['severity'] = 'HIGH'
        
        # Check file content
        if content:
            content_ok, content_issues = self.check_file_content(content, file_path)
            if not content_ok:
                result['issues'].extend(content_issues)
                result['status'] = 'BLOCK'
                result['severity'] = 'CRITICAL' if any('Token' in i or 'Key' in i for i in content_issues) else 'HIGH'
            
            # Check file size
            size_ok, size_issues = self.check_file_size(len(content))
            if not size_ok:
                result['issues'].extend(size_issues)
                result['status'] = 'BLOCK'
                result['severity'] = 'MEDIUM'
        
        # Update stats
        if result['status'] == 'BLOCK':
            self.stats['blocked'] += 1
        elif result['issues']:
            self.stats['warnings'] += 1
        else:
            self.stats['passed'] += 1
        
        return result
    
    def scan_directory(self, dir_path: str) -> List[Dict]:
        """Scan all files in directory"""
        results = []
        
        for root, dirs, files in os.walk(dir_path):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, dir_path)
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    result = self.scan_file(rel_path, content)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error scanning {file_path}: {e}")
                    results.append({
                        'file': rel_path,
                        'status': 'ERROR',
                        'issues': [str(e)],
                        'severity': 'NONE',
                    })
        
        return results


# ============================================================================
# Git Hook Integration
# ============================================================================

class GitHookInstaller:
    """Install Git hooks for pre-commit scanning"""
    
    PRE_COMMIT_HOOK = '''#!/usr/bin/env python3
"""Git Pre-Commit Hook - Auto-installed by Git Firewall Proxy"""

import subprocess
import sys
import os

def get_staged_files():
    """Get list of staged files"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\\n') if result.stdout.strip() else []

def scan_file(file_path):
    """Scan a single file"""
    if not os.path.exists(file_path):
        return {'file': file_path, 'status': 'SKIP', 'issues': []}
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Import detection engine
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from git_firewall_proxy import DetectionEngine, FirewallConfig
        
        engine = DetectionEngine(FirewallConfig())
        return engine.scan_file(file_path, content)
    except Exception as e:
        return {'file': file_path, 'status': 'ERROR', 'issues': [str(e)]}

def main():
    print("🔒 Git Firewall - Pre-Commit Scan")
    print("=" * 50)
    
    staged_files = get_staged_files()
    if not staged_files:
        print("No staged files to scan.")
        sys.exit(0)
    
    print(f"Scanning {len(staged_files)} staged file(s)...\\n")
    
    results = []
    for file_path in staged_files:
        result = scan_file(file_path)
        results.append(result)
        
        status_icon = "✅" if result['status'] == 'PASS' else "🚨"
        print(f"{status_icon} {file_path}: {result['status']}")
        if result['issues']:
            for issue in result['issues']:
                print(f"   ⚠️  {issue}")
    
    print("\\n" + "=" * 50)
    
    # Check for blocks
    blocked = [r for r in results if r['status'] == 'BLOCK']
    if blocked:
        print(f"\\n🚨 BLOCKED: {len(blocked)} file(s) contain sensitive data!")
        print("\\nCommit rejected. Please remove sensitive data before committing.")
        print("\\nTip: Add sensitive files to .gitignore")
        sys.exit(1)
    
    print(f"\\n✅ All files passed security scan!")
    sys.exit(0)

if __name__ == '__main__':
    main()
'''
    
    @staticmethod
    def install(repo_path: str = ".") -> bool:
        """Install pre-commit hook"""
        hooks_dir = os.path.join(repo_path, '.git', 'hooks')
        hook_path = os.path.join(hooks_dir, 'pre-commit')
        
        # Create hooks directory if not exists
        os.makedirs(hooks_dir, exist_ok=True)
        
        # Write hook
        with open(hook_path, 'w', encoding='utf-8') as f:
            f.write(GitHookInstaller.PRE_COMMIT_HOOK)
        
        # Make executable
        os.chmod(hook_path, 0o755)
        
        logger.info(f"Pre-commit hook installed at {hook_path}")
        return True


# ============================================================================
# HTTP Proxy Server (for Git over HTTP)
# ============================================================================

class GitProxyHandler(BaseHTTPRequestHandler):
    """HTTP handler for Git proxy"""
    
    engine = DetectionEngine()
    
    def do_POST(self):
        """Handle Git HTTP POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        
        # Read request body
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Scan for sensitive data
        result = self.engine.scan_file('request_body', body)
        
        if result['status'] == 'BLOCK':
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'error': 'Forbidden',
                'message': 'Sensitive data detected',
                'details': result,
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            logger.warning(f"Blocked request: {result['issues']}")
            return
        
        # Forward request to remote (simplified - in production, use proper proxy)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {'status': 'allowed', 'scanned': True}
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        """Custom log format"""
        logger.info(f"{self.address_string()} - {format % args}")


# ============================================================================
# CLI Interface
# ============================================================================

def scan_repo(repo_path: str, output_file: str = None):
    """Scan repository and generate report"""
    print(f"🔒 Git Firewall - Repository Scan")
    print("=" * 60)
    print(f"Repository: {repo_path}")
    print(f"Time: {datetime.now().isoformat()}")
    print("=" * 60 + "\\n")
    
    engine = DetectionEngine()
    results = engine.scan_directory(repo_path)
    
    # Print summary
    print(f"\\n📊 Scan Summary")
    print(f"  Total files: {engine.stats['scanned']}")
    print(f"  ✅ Passed: {engine.stats['passed']}")
    print(f"  ⚠️  Warnings: {engine.stats['warnings']}")
    print(f"  🚨 Blocked: {engine.stats['blocked']}")
    
    # Print blocked files
    blocked = [r for r in results if r['status'] == 'BLOCK']
    if blocked:
        print(f"\\n🚨 Blocked Files ({len(blocked)}):")
        for result in blocked:
            print(f"\\n  {result['file']}")
            print(f"  Severity: {result['severity']}")
            for issue in result['issues']:
                print(f"    - {issue}")
    
    # Generate report
    report = {
        'timestamp': datetime.now().isoformat(),
        'repository': repo_path,
        'stats': engine.stats,
        'results': results,
        'blocked_files': blocked,
    }
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\\n📄 Report saved to: {output_file}")
    
    return report


def start_proxy(port: int = 8080):
    """Start HTTP proxy server"""
    server = HTTPServer(('localhost', port), GitProxyHandler)
    logger.info(f"Git Firewall Proxy started on http://localhost:{port}")
    print(f"\\n🔒 Git Firewall Proxy Server")
    print(f"   URL: http://localhost:{port}")
    print(f"   Status: Running")
    print(f"\\nPress Ctrl+C to stop\\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\n👋 Shutting down...")
        server.shutdown()


def install_hook(repo_path: str = "."):
    """Install Git pre-commit hook"""
    print(f"🔒 Installing Git pre-commit hook...")
    GitHookInstaller.install(repo_path)
    print(f"✅ Hook installed successfully!")
    print(f"\\nTest with: git commit")


def main():
    parser = argparse.ArgumentParser(
        description='Git Firewall Proxy - Real-time sensitive data detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan repository
  python git-firewall-proxy.py --scan /path/to/repo
  
  # Start proxy server
  python git-firewall-proxy.py --proxy --port 8080
  
  # Install pre-commit hook
  python git-firewall-proxy.py --install-hook
  
  # Scan and generate report
  python git-firewall-proxy.py --scan . --output report.json
        """
    )
    
    parser.add_argument('--scan', type=str, help='Scan repository path')
    parser.add_argument('--proxy', action='store_true', help='Start HTTP proxy server')
    parser.add_argument('--port', type=int, default=8080, help='Proxy server port')
    parser.add_argument('--install-hook', action='store_true', help='Install Git pre-commit hook')
    parser.add_argument('--output', type=str, help='Output report file (JSON)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.scan:
        scan_repo(args.scan, args.output)
    elif args.proxy:
        start_proxy(args.port)
    elif args.install_hook:
        install_hook()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
