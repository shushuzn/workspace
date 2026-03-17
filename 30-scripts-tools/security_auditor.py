#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Security Auditor - Automated Security Scanning
Scans codebase for security vulnerabilities and best practices
Features: Secret detection, code analysis, dependency check, compliance report

Usage:
    python security_auditor.py --scan
    python security_auditor.py --secrets
    python security_auditor.py --dependencies
    python security_auditor.py --report
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

# Workspace root
WORKSPACE = Path(__file__).parent.parent

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


@dataclass
class SecurityIssue:
    """Security issue found"""
    id: str
    severity: str  # critical/high/medium/low/info
    category: str
    file: str
    line: int
    description: str
    recommendation: str
    code_snippet: str


@dataclass
class SecretFound:
    """Secret detected"""
    type: str
    file: str
    line: int
    hash: str  # Hash of secret for tracking
    severity: str


class SecurityAuditor:
    """Automated security auditor"""
    
    def __init__(self):
        self.results_file = WORKSPACE / "20-data-reports" / "security_audit_results.json"
        self.history_file = WORKSPACE / "20-data-reports" / "security_audit_history.json"
        
        self.issues = []
        self.secrets = []
        self.history = []
        
        # Patterns for secret detection
        self.secret_patterns = {
            'api_key': r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']',
            'password': r'(?:password|passwd|pwd)\s*[:=]\s*["\'](.{8,})["\']',
            'secret': r'(?:secret|secret_key)\s*[:=]\s*["\']([a-zA-Z0-9]{16,})["\']',
            'token': r'(?:token|auth_token|access_token)\s*[:=]\s*["\']([a-zA-Z0-9._-]{20,})["\']',
            'private_key': r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
            'aws_key': r'(?:AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}',
            'github_token': r'gh[pousr]_[A-Za-z0-9_]{36,}',
            'database_url': r'(?:mongodb|postgres|mysql|redis)://[^:]+:[^@]+@',
        }
        
        # Security best practices checks
        self.security_checks = {
            'hardcoded_paths': r'[C-Z]:\\[^"\']+',
            'eval_usage': r'\beval\s*\(',
            'exec_usage': r'\bexec\s*\(',
            'shell_injection': r'os\.system\s*\(|subprocess\.call\s*\([^)]*\+|subprocess\.run\s*\([^)]*\+',
            'insecure_deserialize': r'pickle\.loads?\s*\(|yaml\.load\s*\([^)]*\)',
            'sql_injection': r'execute\s*\([^)]*%|execute\s*\([^)]*\+',
            'weak_crypto': r'\b(MD5|SHA1|DES)\b',
            'debug_mode': r'DEBUG\s*=\s*True|debug\s*=\s*True',
        }
    
    def scan_secrets(self, directory: Path = None) -> List[SecretFound]:
        """Scan for secrets in codebase"""
        print("\n" + "="*60)
        print(" Scanning for Secrets")
        print("="*60 + "\n")
        
        if directory is None:
            directory = WORKSPACE
        
        secrets = []
        files_scanned = 0
        
        # Scan Python files
        for py_file in directory.rglob("*.py"):
            # Skip virtual environments and common exclude dirs
            if any(part in str(py_file) for part in ['venv', '.venv', 'node_modules', '__pycache__', '.git']):
                continue
            
            files_scanned += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for secret_type, pattern in self.secret_patterns.items():
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        
                        if matches:
                            # Create hash of secret for tracking (don't store actual secret)
                            secret_hash = hashlib.sha256(str(matches[0]).encode()).hexdigest()[:16]
                            
                            secret = SecretFound(
                                type=secret_type,
                                file=str(py_file.relative_to(WORKSPACE)),
                                line=line_num,
                                hash=secret_hash,
                                severity=self._get_secret_severity(secret_type)
                            )
                            secrets.append(secret)
                            
                            print(f"🔴 [{secret.severity.upper()}] {secret_type} found in {secret.file}:{line_num}")
            
            except Exception as e:
                print(f"⚠️  Error scanning {py_file}: {e}")
        
        # Also scan .env files
        for env_file in directory.rglob(".env*"):
            if any(part in str(env_file) for part in ['venv', '.venv', 'node_modules']):
                continue
            
            files_scanned += 1
            
            try:
                with open(env_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    if '=' in line and not line.strip().startswith('#'):
                        # Check if line contains sensitive variable names
                        sensitive_vars = ['PASSWORD', 'SECRET', 'TOKEN', 'KEY', 'API_KEY', 'PRIVATE']
                        if any(var in line.upper() for var in sensitive_vars):
                            secret = SecretFound(
                                type='env_variable',
                                file=str(env_file.relative_to(WORKSPACE)),
                                line=line_num,
                                hash=hashlib.sha256(line.strip().encode()).hexdigest()[:16],
                                severity='high'
                            )
                            secrets.append(secret)
                            print(f"🔴 [HIGH] Environment variable in {secret.file}:{line_num}")
            
            except Exception as e:
                print(f"⚠️  Error scanning {env_file}: {e}")
        
        self.secrets = secrets
        
        print(f"\n✅ Files scanned: {files_scanned}")
        print(f"🔴 Secrets found: {len(secrets)}\n")
        
        return secrets
    
    def _get_secret_severity(self, secret_type: str) -> str:
        """Get severity for secret type"""
        critical = ['private_key', 'aws_key', 'database_url']
        high = ['password', 'secret', 'token', 'api_key', 'github_token']
        
        if secret_type in critical:
            return 'critical'
        elif secret_type in high:
            return 'high'
        else:
            return 'medium'
    
    def scan_code_security(self, directory: Path = None) -> List[SecurityIssue]:
        """Scan code for security issues"""
        print("\n" + "="*60)
        print(" Scanning Code Security")
        print("="*60 + "\n")
        
        if directory is None:
            directory = WORKSPACE / "30-scripts-tools"
        
        issues = []
        files_scanned = 0
        
        for py_file in directory.rglob("*.py"):
            if any(part in str(py_file) for part in ['venv', '.venv', 'node_modules', '__pycache__']):
                continue
            
            files_scanned += 1
            
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for check_name, pattern in self.security_checks.items():
                        if re.search(pattern, line):
                            issue = SecurityIssue(
                                id=f"sec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(issues)}",
                                severity=self._get_check_severity(check_name),
                                category=check_name,
                                file=str(py_file.relative_to(WORKSPACE)),
                                line=line_num,
                                description=f"Potential {check_name.replace('_', ' ')} detected",
                                recommendation=self._get_recommendation(check_name),
                                code_snippet=line.strip()[:100]
                            )
                            issues.append(issue)
            
            except Exception as e:
                print(f"⚠️  Error scanning {py_file}: {e}")
        
        self.issues = issues
        
        # Print summary
        by_severity = {}
        for issue in issues:
            by_severity[issue.severity] = by_severity.get(issue.severity, 0) + 1
        
        print(f"✅ Files scanned: {files_scanned}")
        print(f"\nIssues found:")
        for severity, count in sorted(by_severity.items()):
            icon = "🔴" if severity == 'critical' else "🟠" if severity == 'high' else "🟡"
            print(f"  {icon} {severity.upper()}: {count}")
        print()
        
        return issues
    
    def _get_check_severity(self, check_name: str) -> str:
        """Get severity for security check"""
        critical = ['private_key', 'sql_injection', 'shell_injection']
        high = ['eval_usage', 'exec_usage', 'insecure_deserialize', 'weak_crypto']
        medium = ['hardcoded_paths', 'debug_mode']
        
        if check_name in critical:
            return 'critical'
        elif check_name in high:
            return 'high'
        elif check_name in medium:
            return 'medium'
        else:
            return 'low'
    
    def _get_recommendation(self, check_name: str) -> str:
        """Get recommendation for security issue"""
        recommendations = {
            'hardcoded_paths': 'Use pathlib.Path and relative paths instead of hardcoded absolute paths',
            'eval_usage': 'Avoid eval(). Use ast.literal_eval() for safe evaluation or refactor logic',
            'exec_usage': 'Avoid exec(). Refactor to use functions or safer alternatives',
            'shell_injection': 'Use subprocess with shell=False and pass arguments as list',
            'insecure_deserialize': 'Use json.loads() instead of pickle. For YAML, use yaml.safe_load()',
            'sql_injection': 'Use parameterized queries instead of string formatting',
            'weak_crypto': 'Use SHA-256 or stronger. For passwords, use bcrypt or argon2',
            'debug_mode': 'Disable debug mode in production. Use environment variables to control',
        }
        
        return recommendations.get(check_name, 'Review and fix this security issue')
    
    def check_dependencies(self) -> Dict:
        """Check dependencies for known vulnerabilities"""
        print("\n" + "="*60)
        print(" Checking Dependencies")
        print("="*60 + "\n")
        
        requirements_file = WORKSPACE / "requirements.txt"
        
        if not requirements_file.exists():
            print("⚠️  requirements.txt not found")
            return {'error': 'No requirements.txt found'}
        
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            print(f"✅ Dependencies found: {len(dependencies)}\n")
            
            # In production, would check against vulnerability database
            # For now, just list them
            for dep in dependencies:
                print(f"  • {dep}")
            
            return {
                'total': len(dependencies),
                'dependencies': dependencies,
                'vulnerabilities': []  # Would populate from vulnerability DB
            }
        
        except Exception as e:
            print(f"❌ Error: {e}")
            return {'error': str(e)}
    
    def generate_report(self) -> str:
        """Generate security audit report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = WORKSPACE / "20-data-reports" / f"security_audit_{timestamp}.md"
        
        # Run scans if not already done
        if not self.secrets:
            self.scan_secrets()
        if not self.issues:
            self.scan_code_security()
        
        # Calculate summary
        total_issues = len(self.secrets) + len(self.issues)
        critical = sum(1 for s in self.secrets if s.severity == 'critical') + \
                   sum(1 for i in self.issues if i.severity == 'critical')
        high = sum(1 for s in self.secrets if s.severity == 'high') + \
               sum(1 for i in self.issues if i.severity == 'high')
        medium = sum(1 for s in self.secrets if s.severity == 'medium') + \
                 sum(1 for i in self.issues if i.severity == 'medium')
        low = sum(1 for i in self.issues if i.severity == 'low')
        
        # Calculate security score
        max_score = 100
        deductions = (critical * 20) + (high * 10) + (medium * 5) + (low * 2)
        security_score = max(0, max_score - deductions)
        
        report = f"""# Security Audit Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version:** 1.0

## Executive Summary

- **Security Score:** {security_score}/100 {'✅ Good' if security_score >= 80 else '⚠️ Needs Improvement' if security_score >= 50 else '❌ Critical'}
- **Total Issues:** {total_issues}
- **Critical:** {critical}
- **High:** {high}
- **Medium:** {medium}
- **Low:** {low}

---

## Secrets Detection

**Total Secrets Found:** {len(self.secrets)}

"""
        
        if self.secrets:
            report += "| Type | File | Line | Severity |\n"
            report += "|------|------|------|----------|\n"
            
            for secret in self.secrets:
                report += f"| {secret.type} | {secret.file} | {secret.line} | {secret.severity} |\n"
        else:
            report += "✅ No secrets detected\n"
        
        report += f"""
---

## Code Security Issues

**Total Issues:** {len(self.issues)}

"""
        
        if self.issues:
            # Group by severity
            for severity in ['critical', 'high', 'medium', 'low']:
                severity_issues = [i for i in self.issues if i.severity == severity]
                
                if severity_issues:
                    report += f"### {severity.upper()} ({len(severity_issues)})\n\n"
                    
                    for issue in severity_issues[:10]:  # Limit to 10 per severity
                        report += f"#### {issue.id}\n\n"
                        report += f"- **File:** {issue.file}:{issue.line}\n"
                        report += f"- **Category:** {issue.category}\n"
                        report += f"- **Description:** {issue.description}\n"
                        report += f"- **Recommendation:** {issue.recommendation}\n"
                        if issue.code_snippet:
                            report += f"- **Code:** `{issue.code_snippet}`\n"
                        report += "\n"
        else:
            report += "✅ No code security issues detected\n"
        
        report += f"""
---

## Recommendations

### Immediate Actions (Critical/High)

"""
        
        critical_high = [i for i in self.issues if i.severity in ['critical', 'high']]
        critical_high_secrets = [s for s in self.secrets if s.severity in ['critical', 'high']]
        
        if critical_high or critical_high_secrets:
            for i, issue in enumerate(critical_high[:5], 1):
                report += f"{i}. **{issue.file}:{issue.line}** - {issue.description}\n"
                report += f"   → {issue.recommendation}\n\n"
            
            for i, secret in enumerate(critical_high_secrets[:5], len(critical_high) + 1):
                report += f"{i}. **{secret.file}:{secret.line}** - {secret.type} detected\n"
                report += f"   → Remove secret and use environment variables\n\n"
        else:
            report += "✅ No critical or high priority issues\n"
        
        report += f"""
### Best Practices

1. Use environment variables for all sensitive configuration
2. Implement secret rotation policies
3. Enable pre-commit hooks for secret detection
4. Regular security audits (monthly recommended)
5. Keep dependencies updated
6. Use dependency scanning tools (safety, dependabot)

---

## Next Steps

1. Address all critical issues immediately
2. Fix high priority issues within 1 week
3. Schedule medium priority fixes
4. Monitor low priority issues

---

*Report generated by Security Auditor v1.0*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Report saved: {report_file}")
        print(f"\nSecurity Score: {security_score}/100\n")
        
        # Save results
        results = {
            'timestamp': datetime.now().isoformat(),
            'security_score': security_score,
            'total_issues': total_issues,
            'by_severity': {
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            },
            'secrets': [asdict(s) for s in self.secrets],
            'issues': [asdict(i) for i in self.issues]
        }
        
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Record to history
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'security_score': security_score,
            'total_issues': total_issues
        })
        self.history = self.history[-20:]
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump({'history': self.history}, f, indent=2, ensure_ascii=False)
        
        return report
    
    def get_summary(self) -> Dict:
        """Get audit summary"""
        return {
            'total_secrets': len(self.secrets),
            'total_issues': len(self.issues),
            'by_severity': {
                'critical': sum(1 for s in self.secrets if s.severity == 'critical') + 
                           sum(1 for i in self.issues if i.severity == 'critical'),
                'high': sum(1 for s in self.secrets if s.severity == 'high') + 
                       sum(1 for i in self.issues if i.severity == 'high'),
                'medium': sum(1 for s in self.secrets if s.severity == 'medium') + 
                         sum(1 for i in self.issues if i.severity == 'medium'),
                'low': sum(1 for i in self.issues if i.severity == 'low')
            },
            'last_audit': self.history[-1] if self.history else None
        }


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Security Auditor')
    parser.add_argument('--scan', action='store_true', help='Full security scan')
    parser.add_argument('--secrets', action='store_true', help='Scan for secrets')
    parser.add_argument('--code', action='store_true', help='Scan code security')
    parser.add_argument('--dependencies', action='store_true', help='Check dependencies')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--status', action='store_true', help='Show status')
    args = parser.parse_args()
    
    auditor = SecurityAuditor()
    
    if args.scan:
        auditor.scan_secrets()
        auditor.scan_code_security()
        auditor.check_dependencies()
    
    elif args.secrets:
        secrets = auditor.scan_secrets()
        print(f"\nTotal: {len(secrets)} secrets found")
    
    elif args.code:
        issues = auditor.scan_code_security()
        print(f"\nTotal: {len(issues)} issues found")
    
    elif args.dependencies:
        result = auditor.check_dependencies()
        print(json.dumps(result, indent=2))
    
    elif args.report:
        auditor.generate_report()
    
    elif args.status:
        status = auditor.get_summary()
        print(json.dumps(status, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
